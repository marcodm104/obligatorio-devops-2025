import boto3                    # SDK de AWS para Python
import os                       # Manejo de archivos y directorios locales
import time                     # Pausa para esperar recursos
from botocore.exceptions import ClientError   # Para manejar errores de AWS

# ========================
# Variables globales
# ========================

BUCKET_NAME = input("Ingrese el nombre del bucket S3: ").strip()   # Nombre del bucket S3
LOCAL_FOLDER = './ArchivosWeb'                                     # Carpeta local con archivos de la app
S3_PREFIX = 'appweb/'                                              # Prefijo dentro del bucket
DB_INSTANCE_ID = 'rrhh-rds-instancia'  # Nombre de la instancia RDS
DB_USERNAME = 'admin'                                              # Usuario administrador de la DB
DB_NAME = 'demo_db'                                                # Nombre de la base
DB_PASSWORD = input("Ingrese la contraseña para la base de datos (mínimo 8 caracteres): ").strip()
EC2_IMAGE_ID = 'ami-0fa3fe0fa7920f68e'                             # AMI a utilizar

# Clientes de AWS
ec2_client = boto3.client('ec2')
rds_client = boto3.client('rds')
s3_client = boto3.client('s3')


# =======================================
# Subir archivos al bucket S3
# =======================================
def upload_web_files():
    print("\nSubiendo archivos web al bucket S3...")

    # Verifica que la carpeta exista
    if not os.path.isdir(LOCAL_FOLDER):
        print(f"La carpeta NO existe: {LOCAL_FOLDER}")
        exit(1)

    try:
        # Intenta crear el bucket
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket creado correctamente: {BUCKET_NAME}")
    except Exception as e:
        # Si ya existe y es del usuario, se reutiliza
        if "BucketAlreadyOwnedByYou" in str(e):
            print("ℹ El bucket ya existe y es de su propiedad.")

    # Recorre recursivamente todos los archivos dentro de LOCAL_FOLDER
    for root, dirs, files in os.walk(LOCAL_FOLDER):
        for filename in files:
            local_path = os.path.join(root, filename)    # Ruta completa local
            # Ruta relativa respecto a LOCAL_FOLDER (para mantener estructura)
            s3_key = os.path.relpath(local_path, LOCAL_FOLDER).replace("\\", "/")
            # Ruta final en S3: appweb/<ruta_relativa>
            s3_path = f"{S3_PREFIX}{s3_key}"

            print(f"Subiendo: {local_path} -> s3://{BUCKET_NAME}/{s3_path}")
            s3_client.upload_file(local_path, BUCKET_NAME, s3_path)  # Subir archivo

    print("Archivos web subidos exitosamente al bucket S3.\n")


# ===============================================================
# Crear un Security Group (SG) con reglas de ingreso especificadas
# ===============================================================
def create_security_group(group_name, description, ingress_rules):
    group_id = None
    try:
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description
        )
        group_id = response['GroupId']                   # ID del SG creado

        ec2_client.authorize_security_group_ingress(     # Agregar reglas
            GroupId=group_id,
            IpPermissions=ingress_rules
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            # Si el SG ya existe, recuperamos su ID
            existing = ec2_client.describe_security_groups(GroupNames=[group_name])
            group_id = existing['SecurityGroups'][0]['GroupId']
    return group_id


# ===============================================================
# Configurar los SG para Web y Base de Datos
# ===============================================================
def setup_security_groups():
    # SG para el servidor web
    web_sg_name = 'rrhh-web-sg'
    web_sg_id = create_security_group(
        web_sg_name,
        'Grupo de seguridad para el servidor web RRHH',
        [
            {
                'IpProtocol': 'tcp',                     # Protocolo HTTP
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]    # Acceso público
            }
        ]
    )

    # SG para RDS que solo permite tráfico desde el SG Web
    db_sg_name = 'rrhh-db-sg'
    db_sg_id = create_security_group(
        db_sg_name,
        'Grupo de seguridad para la base de datos RRHH',
        [
            {
                'IpProtocol': 'tcp',
                'FromPort': 3306,
                'ToPort': 3306,
                'UserIdGroupPairs': [{'GroupId': web_sg_id}]   # Solo EC2 Web accede
            }
        ]
    )

    return web_sg_id, db_sg_id


# ===============================================================
# Crear instancia RDS MySQL
# ===============================================================
def create_rds_instance(db_sg_id):
    try:
        rds_client.create_db_instance(
            DBInstanceIdentifier=DB_INSTANCE_ID,
            DBInstanceClass='db.t3.micro',
            Engine='mysql',
            MasterUsername=DB_USERNAME,
            MasterUserPassword=DB_PASSWORD,
            DBName=DB_NAME,
            AllocatedStorage=20,
            StorageType='gp2',
            StorageEncrypted=True,               # Cifrado en reposo
            VpcSecurityGroupIds=[db_sg_id],      # SG asociado
            BackupRetentionPeriod=7,             # Backups automáticos
            PubliclyAccessible=True              # En el lab, esto puede ser True
        )
        print("Instancia RDS creada: esperando a que esté disponible...")

        waiter = rds_client.get_waiter('db_instance_available')  # Espera hasta que RDS esté lista
        waiter.wait(DBInstanceIdentifier=DB_INSTANCE_ID)

    except ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceAlreadyExists':
            print(f"ℹ La instancia RDS ya existe: {DB_INSTANCE_ID}")
        else:
            print("Error creando la instancia RDS:", e)
            raise

    info = rds_client.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
    return info['DBInstances'][0]['Endpoint']['Address']   # Retorna el endpoint


# ===============================================================
# Generar script User Data para inicializar EC2
# ===============================================================
def generate_userdata_script(db_endpoint):
    # Este script se ejecuta automáticamente cuando EC2 inicia.
    return f'''#!/bin/bash
yum update -y
yum install -y httpd php php-cli php-fpm php-common php-mysqlnd mariadb105 awscli

systemctl enable --now httpd
systemctl enable --now php-fpm

# Configurar PHP-FPM con Apache
echo '<FilesMatch \\\\.php$>
  SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost/"
</FilesMatch>' | tee /etc/httpd/conf.d/php-fpm.conf

rm -rf /var/www/html/*

# Sincroniza desde appweb/ (coincide con S3_PREFIX)
aws s3 sync s3://{BUCKET_NAME}/appweb/ /var/www/html/

# Copiar SQL inicial si existe
if [ -f /var/www/html/init_db.sql ]; then
  cp /var/www/html/init_db.sql /var/www/
fi

# Crear archivo .env con credenciales
if [ ! -f /var/www/.env ]; then
cat > /var/www/.env << 'EOT'
DB_HOST={db_endpoint}
DB_NAME={DB_NAME}
DB_USER={DB_USERNAME}
DB_PASS={DB_PASSWORD}
EOT
fi

chown apache:apache /var/www/.env
chmod 600 /var/www/.env

chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Ejecutar script SQL inicial si está presente
if [ -f /var/www/init_db.sql ]; then
  mysql -h {db_endpoint} -u {DB_USERNAME} -p{DB_PASSWORD} {DB_NAME} < /var/www/init_db.sql
fi

systemctl restart httpd php-fpm
'''


# ===============================================================
# Lanzar instancia EC2
# ===============================================================
def launch_ec2_instance(web_sg_id, userdata_script):
    response = ec2_client.run_instances(
        ImageId=EC2_IMAGE_ID,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        IamInstanceProfile={'Name': 'LabInstanceProfile'},
        SecurityGroupIds=[web_sg_id],
        UserData=userdata_script,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 8,
                    'VolumeType': 'gp2',
                    'Encrypted': True
                }
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']

    # Etiquetas
    ec2_client.create_tags(
        Resources=[instance_id],
        Tags=[
            {'Key': 'Name', 'Value': 'app-rrhh'},
            {'Key': 'Application', 'Value': 'RRHH'},
            {'Key': 'DataClassification', 'Value': 'Confidencial'}
        ]
    )

    return instance_id


# ===============================================================
# Obtener IP pública de una EC2
# ===============================================================
def get_instance_public_ip(instance_id):
    print("\nObteniendo la dirección IP pública de la instancia EC2...")
    time.sleep(15)  # Espera básica para que la IP se asigne y los servicios levanten
    info = ec2_client.describe_instances(InstanceIds=[instance_id])
    return info['Reservations'][0]['Instances'][0].get('PublicIpAddress')


# ===============================================================
# Función principal
# ===============================================================
def main():
    upload_web_files()                               # Subir app a S3
    web_sg_id, db_sg_id = setup_security_groups()    # Crear SGs
    db_endpoint = create_rds_instance(db_sg_id)      # Crear RDS y obtener endpoint
    userdata = generate_userdata_script(db_endpoint) # Generar User Data
    instance_id = launch_ec2_instance(web_sg_id, userdata)  # Lanzar EC2
    public_ip = get_instance_public_ip(instance_id)  # Obtener IP pública

    print(f"\nURL de acceso a la aplicación web: http://{public_ip}/login.php")
    print("====================================")


if __name__ == "__main__":
    main()

