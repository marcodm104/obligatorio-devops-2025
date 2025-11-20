#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# ------------------ Funciones auxiliares locales ------------------ #

def leer_config(ruta_config):
    """
    Lee un archivo de configuración tipo CLAVE=valor
    y devuelve un diccionario.
    Ignora líneas vacías y comentarios que empiezan con #.
    """
    config = {}
    with open(ruta_config, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split("=", 1)
            if len(partes) != 2:
                continue
            clave = partes[0].strip()
            valor = partes[1].strip()
            config[clave] = valor
    return config


def asegurar_directorio(ruta_dir):
    """
    Crea el directorio si no existe.
    """
    if not os.path.exists(ruta_dir):
        os.makedirs(ruta_dir)


def registrar_log(ruta_log, mensaje):
    """
    Agrega una línea al archivo de log con fecha y hora.
    """
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca_tiempo}] {mensaje}\n"
    with open(ruta_log, "a", encoding="utf-8") as f:
        f.write(linea)


def crear_archivo_empleados(ruta_empleados, modo_demo):
    """
    Crea el archivo empleados.csv si no existe.
    Si modo_demo == 'SI', crea datos de prueba.
    Si modo_demo == 'NO', solo crea el encabezado.
    Devuelve la cantidad de registros creados (no cuenta el encabezado).
    """
    if os.path.exists(ruta_empleados):
        # ya existe, no se pisa para no romper datos reales
        return 0

    encabezado = "nombre,email,salario\n"
    datos_demo = [
        "Alicia,a@ejemplo.com,50000\n",
        "Bruno,b@ejemplo.com,60000\n",
        "Carla,c@ejemplo.com,70000\n",
    ]

    with open(ruta_empleados, "w", encoding="utf-8") as f:
        f.write(encabezado)
        if modo_demo.upper() == "SI":
            for linea in datos_demo:
                f.write(linea)
            cantidad = len(datos_demo)
        else:
            cantidad = 0

    return cantidad


def proteger_archivo_sensible(ruta):
    """
    Intenta poner permisos 600 (rw-------) al archivo.
    Si falla por permisos, no corta el programa.
    """
    try:
        os.chmod(ruta, 0o600)
    except PermissionError:
        # no tenemos permisos suficientes, lo dejamos pasar
        pass
    
# ------------------ Funciones AWS (S3 y RDS) ------------------ #

def asegurar_bucket_y_subir(aws_region, bucket_name,
                             app_package_path, s3_app_key,
                             empleados_path, s3_empleados_key,
                             ruta_log):
    """
    Crea (si hace falta) el bucket S3 y sube:
    - paquete de la app
    - archivo de empleados
    """
    s3 = boto3.client("s3", region_name=aws_region if aws_region else None)

    # Verificar/crear bucket
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"El bucket '{bucket_name}' ya existe.")
        registrar_log(ruta_log, f"Bucket S3 {bucket_name} ya existía.")
    except ClientError:
        # intentar crearlo
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket creado: {bucket_name}")
            registrar_log(ruta_log, f"Bucket S3 {bucket_name} creado.")
        except ClientError as e:
            print(f"Error creando bucket: {e}")
            registrar_log(ruta_log, f"ERROR creando bucket {bucket_name}: {e}")
            raise

    # Subir paquete de aplicación
    if not os.path.exists(app_package_path):
        raise FileNotFoundError(f"El paquete de la app no existe: {app_package_path}")

    try:
        s3.upload_file(app_package_path, bucket_name, s3_app_key)
        print(f"Paquete app subido a s3://{bucket_name}/{s3_app_key}")
        registrar_log(ruta_log, f"Subido paquete app a s3://{bucket_name}/{s3_app_key}")
    except ClientError as e:
        print(f"Error subiendo paquete de la app: {e}")
        registrar_log(ruta_log, f"ERROR subiendo paquete app: {e}")
        raise

    # Subir archivo de empleados (datos sensibles)
    if not os.path.exists(empleados_path):
        raise FileNotFoundError(f"El archivo de empleados no existe: {empleados_path}")

    try:
        s3.upload_file(empleados_path, bucket_name, s3_empleados_key)
        print(f"Archivo de empleados subido a s3://{bucket_name}/{s3_empleados_key}")
        registrar_log(ruta_log, f"Subido empleados a s3://{bucket_name}/{s3_empleados_key}")
    except ClientError as e:
        print(f"Error subiendo archivo de empleados: {e}")
        registrar_log(ruta_log, f"ERROR subiendo empleados: {e}")
        raise


def asegurar_instancia_rds(aws_region, instancia_id, db_name, db_user, ruta_log):
    """
    Crea la instancia RDS MySQL si no existe.
    La contraseña del admin se toma de la variable de entorno RDS_ADMIN_PASSWORD.
    """
    db_pass = os.environ.get("RDS_ADMIN_PASSWORD")
    if not db_pass:
        raise Exception(
            "Debe definirse la variable de entorno RDS_ADMIN_PASSWORD con la contraseña del admin."
        )

    rds = boto3.client("rds", region_name=aws_region if aws_region else None)

    # ¿Ya existe la instancia?
    try:
        rds.describe_db_instances(DBInstanceIdentifier=instancia_id)
        print(f"La instancia RDS '{instancia_id}' ya existe.")
        registrar_log(ruta_log, f"Instancia RDS {instancia_id} ya existente.")
        return
    except rds.exceptions.DBInstanceNotFoundFault:
        print(f"La instancia RDS '{instancia_id}' no existe. Creándola...")
        registrar_log(ruta_log, f"Creando instancia RDS {instancia_id}...")

    try:
        rds.create_db_instance(
            DBInstanceIdentifier=instancia_id,
            AllocatedStorage=20,
            DBInstanceClass="db.t3.micro",
            Engine="mysql",
            MasterUsername=db_user,
            MasterUserPassword=db_pass,
            DBName=db_name,
            PubliclyAccessible=False,  # más seguro
            BackupRetentionPeriod=0,
        )
        print(f"Instancia RDS {instancia_id} creada correctamente.")
        registrar_log(ruta_log, f"Instancia RDS {instancia_id} creada correctamente.")
    except rds.exceptions.DBInstanceAlreadyExistsFault:
        print(f"La instancia {instancia_id} ya existe.")
        registrar_log(ruta_log, f"Instancia RDS {instancia_id} ya existía (create_db_instance).")
    except Exception as e:
        print(f"Error creando la instancia RDS: {e}")
        registrar_log(ruta_log, f"ERROR creando RDS {instancia_id}: {e}")
        raise
