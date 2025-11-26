Obligatorio Programación para DevOps 2025

Integrantes: Marco Di Mella (270830), Juan Felipe Scremini (267261)

Carrera: Analista en Infraestructura Informática – Universidad ORT Uruguay
Año: 2025

Descripción general del proyecto

Este repositorio contiene la solución completa del Obligatorio de Programación para DevOps 2025, compuesto por:

Ejercicio 1 (Bash)

Script que automatiza la creación de usuarios en Linux a partir de un archivo de entrada, aplicando verificaciones, manejo de errores y opciones adicionales de ejecución.

Ejercicio 2 (Python + AWS)

Automatización del despliegue de una aplicación de Recursos Humanos, la cual trabaja con datos sensibles (nombres, emails, salarios).

Incluye:

Preparación del entorno local

Creación de carpetas, logs y archivo de empleados

Protección de datos sensibles

Subida de artefactos a AWS S3

Creación de una base de datos MySQL en AWS RDS

Uso completo de configuraciones externas (config_rrhh.env)

Trazabilidad mediante GitHub


Estructura del repositorio:

```bash
obligatorio-devops-2025/
├── ejercicio1/
│   ├── ej1_crea_usuarios.sh
│   ├── usuarios.txt
│   └── Salida_ejecucion.png
│
├── ejercicio2/
│   ├── ejercicio2.py
│   ├── config_rrhh.env.ejemplo
│   ├── rrhh_app/
│   │   ├── datos/
│   │   │   └── empleados.csv
│   │   └── logs/
│   │       └── deploy.log
│   └── .gitkeep
│
├── Docs/
│   └── img/
│       ├── ejecucion_powershell_local.png
│       ├── ejecucion_powershell_aws.png
│       ├── rds_detalle.png
│       ├── rds_instancia.png
│       ├── s3_app_carpeta.png
│       ├── s3_bucket.png
│       ├── s3_bucket_estructura.png
│       └── s3_data_carpeta.png
│
├── .gitignore
└── README.md
     
```

Link del repositorio: https://github.com/marcodm104/obligatorio-devops-2025

Requisitos / Dependencias

Ejercicio 1 (Bash)

Debe ejecutarse en un entorno Linux con:
- bash 4.x o superior
- permisos para crear usuarios
- archivo de entrada con formato: nombre:comentario:/home/directorio:SI|NO

------------------------------------------------------------------------

Uso del script

ejecución del script:

./ej1_crea_usuarios.sh [-i] [-c contraseña] archivo_usuarios

Formato del archivo de entrada (usuarios.txt):

Cada línea debe contener 5 campos, separados por “:”

ejemplo:

usuario:comentario:home:SI|NO:shell

------------------------------------------------------------------------

El script utiliza códigos de salida específicos para identificar fallas:

| Código | Motivo     | Descripción                               |
|--------|------------|--------------------------------------------|
| 10     | Parámetros | Cantidad incorrecta de parámetros          |
| 11     | Parámetros | Falta contraseña tras -c                   |
| 12     | Parámetros | Modificador inválido                       |
| 13     | Archivo    | No se proporcionó archivo de entrada       |
| 20     | Archivo    | El archivo no existe                       |
| 21     | Archivo    | El archivo no es regular                   |
| 22     | Archivo    | Sin permisos de lectura                    |
| 30     | Formato    | Cantidad incorrecta de campos              |
| 31     | Formato    | Campo "SI/NO" inválido                     |

------------------------------------------------------------------------

Ubicacion del script en el sistema:

C:\Users\Marco Aurelio\Documents\devops\obligatorio-devops-2025\ejercicio1

------------------------------------------------------------------------

Ejemplo salida real de la ejecución.

El script fue probado en una máquina virtual Centos 8.1, verificando su correcto funcionamiento.

![Salida real del script](ejercicio1/Salida_ejecucion.png)

El script cumple con todos los requisitos solicitados: creación de usuarios, validación de parámetros, manejo de errores, modularidad y evidencia real de ejecución.
La ejecución fue probada en un entorno Linux real, y los usuarios fueron creados correctamente siguiendo el formato establecido.

---------------------------------------------------------------------------------
```bash
Codigo ejercicio 1 (bash)

#!/bin/bash

INFO=0
USAR_PASS=0
PASS=""

# ---- Validar cantidad de parámetros ----
if [ $# -lt 1 ] || [ $# -gt 4 ]; then
    echo "uso: $0 [-i] [-c contraseña] archivo_usuarios" >&2
    exit 10
fi

# ---- Procesar modificadores ----
while [ "${1#-}" != "$1" ]; do
    case "$1" in
        -i)
            INFO=1
            shift
            ;;
        -c)
            if [ -z "$2" ]; then
                echo "Error: te falta contraseña" >&2
                exit 11
            fi
            USAR_PASS=1
            PASS="$2"
            shift 2
            ;;
        *)
            echo "Error: modificador invalido: $1" >&2
            exit 12
            ;;
    esac
done

# ---- Debe quedar solo el archivo ----
if [ $# -ne 1 ]; then
    echo "Error: Falta el archivo"
    exit 13
fi

ARCHIVO="$1"

# ---- Verificaciones del archivo ----
if [ ! -e "$ARCHIVO" ]; then
    echo "Error: El archivo '$ARCHIVO' no existe" >&2
    exit 20
fi

if [ ! -f "$ARCHIVO" ]; then
    echo "Error: El archivo no es regular." >&2
    exit 21
fi

if [ ! -r "$ARCHIVO" ]; then
    echo "Error: No hay permisos de lectura sobre el archivo." >&2
    exit 22
fi

CREADOS=0

# ---- Bucle principal ----
while IFS= read -r linea
do
    # Saltar líneas vacías
    [ -z "$linea" ] && continue

    # Contar cantidad de ':' (tienen que ser 4)
    CANT_2PUNTOS=$(echo "$linea" | tr -cd ':' | wc -c)
    if [ "$CANT_2PUNTOS" -ne 4 ]; then
        echo "Error: cantidad de campos en linea '$linea' incorrecta" >&2
        exit 30
    fi

    # Partir la línea en 5 campos usando IFS y set
    OLD_IFS="$IFS"
    IFS=':'
    set -- $linea    # ahora: $1=USUARIO, $2=COMENTARIO, $3=HOME, $4=CREAR_HOME, $5=SHELL_DEF
    IFS="$OLD_IFS"

    USUARIO="$1"
    COMENTARIO="$2"
    HOME="$3"
    CREAR_HOME="$4"
    SHELL_DEF="$5"

    # ---- Crear usuario según los campos ----
    # -c "$COMENTARIO" si hay comentario.
    # -d "$HOME" si hay home.
    # -m / -M según se quiera crear o no el home.
    # -s "$SHELL_DEF" si hay shell específica.

    if [ -z "$HOME" ]; then
        # Sin home definido
        if [ -z "$SHELL_DEF" ]; then
            if [ -z "$COMENTARIO" ]; then
                useradd "$USUARIO"
            else
                useradd -c "$COMENTARIO" "$USUARIO"
            fi
        else
            if [ -z "$COMENTARIO" ]; then
                useradd -s "$SHELL_DEF" "$USUARIO"
            else
                useradd -c "$COMENTARIO" -s "$SHELL_DEF" "$USUARIO"
            fi
        fi
    else
        # Con home definido
        if [ "$CREAR_HOME" = "SI" ]; then
            CREAR_DIR="-m"
        elif [ "$CREAR_HOME" = "NO" ]; then
            CREAR_DIR="-M"
        elif [ -z "$CREAR_HOME" ]; then
            CREAR_DIR=""
        else
            echo "Error: el campo crear home tiene un valor invalido: $CREAR_HOME" >&2
            exit 31
        fi

        if [ -z "$SHELL_DEF" ]; then
            if [ -z "$COMENTARIO" ]; then
                useradd $CREAR_DIR -d "$HOME" "$USUARIO"
            else
                useradd $CREAR_DIR -d "$HOME" -c "$COMENTARIO" "$USUARIO"
            fi
        else
            if [ -z "$COMENTARIO" ]; then
                useradd $CREAR_DIR -d "$HOME" -s "$SHELL_DEF" "$USUARIO"
            else
                useradd $CREAR_DIR -d "$HOME" -c "$COMENTARIO" -s "$SHELL_DEF" "$USUARIO"
            fi
        fi
    fi

    RESULTADO=$?   # código de salida de useradd

    if [ "$RESULTADO" -eq 0 ]; then
        CREADOS=$((CREADOS + 1))

        if [ "$USAR_PASS" -eq 1 ]; then
            echo "$USUARIO:$PASS" | chpasswd
        fi

        if [ "$INFO" -eq 1 ]; then
            echo "Usuario $USUARIO fue creado con exito con los siguientes datos:"

            if [ -z "$COMENTARIO" ]; then
                echo "Comentario: Sin comentario"
            else
                echo "Comentario: $COMENTARIO"
            fi

            if [ -z "$HOME" ]; then
                echo "Directorio por defecto"
            else
                echo "Directorio Home: $HOME"
                if [ "$CREAR_HOME" = "SI" ]; then
                    echo "Se aseguro la existencia del directorio home"
                else
                    echo "NO se aseguro la existencia del directorio home"
                fi
            fi

            if [ -z "$SHELL_DEF" ]; then
                echo "Shell por defecto"
            else
                echo "Shell por defecto: $SHELL_DEF"
            fi

            echo
        fi
    else
        if [ "$INFO" -eq 1 ]; then
            echo "El usuario $USUARIO no se pudo crear"
            echo
        fi
    fi
done < "$ARCHIVO"

echo
echo "Se han creado de manera exitosa $CREADOS usuarios"
```

------------------------------------------------------------------------

Requisitos / Dependencias

Ejercicio 2 (Python + AWS)
Requiere:
- Python 3.8+
- Librerías instaladas:
boto3
botocore

Se requiere una cuenta AWS Academy con permisos sobre:

- Amazon S3

- Amazon RDS (MySQL)

Archivo de configuración obligatorio

El script utiliza un archivo externo llamado: config_rrhh.env

BASE_DIR=./rrhh_app
DATOS_DIR=datos
LOGS_DIR=logs
ARCHIVO_EMPLEADOS=empleados.csv
ARCHIVO_LOG=deploy.log
MODO_DEMO=SI

HABILITAR_AWS=NO
AWS_REGION=us-east-1
S3_BUCKET=mi-bucket-devops
APP_PACKAGE=ejercicio2/app_rrhh.zip
S3_APP_KEY=app/app_rrhh.zip
S2_EMPLEADOS_KEY=data/empleados.csv

RDS_DB_INSTANCE_ID=rrhh-mysql
RDS_DB_NAME=rrhh
RDS_DB_USER=admin

Este archivo nos permite:

- Modificar rutas sin tocar el código.

- Activar o desactivar AWS con:
  HABILITAR_AWS=SI o HABILITAR_AWS=NO.

- No contiene contraseñas por temas de seguridad

Antes de ejecutar con AWS, el usuario debe definir:

export RDS_ADMIN_PASSWORD="ContraseñaDificil123!"

Esta variable es utilizada para crear el usuario administrador del motor MySQL en RDS.

------------------------------------------------------------------------

Uso del script

Modo de uso

Ejecución local (sin AWS)

python3 ejercicio2.py

Esto realiza:

Creación de directorios

Creación de empleados.csv

Creación de deploy.log

Aplicación de permisos 600 al archivo sensible

Si lo queremos ejecutar con AWS habilitado

Editar config_rrhh.env:

HABILITAR_AWS=SI


Exportar la contraseña de RDS:

export RDS_ADMIN_PASSWORD="ContraseñaDificil123!"


Ejecutar:

python3 ejercicio2.py

-----------------------------------------------------------------------------

El script realizará:

Verificación o creación del bucket S3.

Subida del ZIP de la app.

Subida del archivo empleados.csv.

Creación de una instancia RDS MySQL segura.

----------------------------------------------------------------------------------

Evidencia de ejecución real del script

Ejecución del script en powershell configurado con aws cli

Ejecución con AWS habilitado:

![Ejecución con AWS](Docs/img/ejecucion_powershell_aws.png)

Se observa:

- Confirmación de que el bucket ya existe.

- Subida de app_rrhh.zip.

- Subida de empleados.csv.

- Creación de la instancia RDS rrhh-mysql.

- Mensaje final indicando que el despliegue local fue completado.

Ejecución Local:

En este caso:

- No se realizan acciones en AWS.

- Se crea la estructura local.

- Se indica la cantidad de registros demo creados.

- Se muestra la ubicación del log de despliegue.

![Ejecución sin AWS](Docs/img/ejecucion_powershell_local.png)

Listado de bases de datos en AWS RDS:

![Instancia RDS creada](Docs/img/rds_instancia.png)

se observa la instancia rrhh-mysql en estado Disponible, motor MySQL y clase db.t3.micro.

Detalle de conectividad y seguridad de la instancia RDS:

![Detalle instancia RDS](Docs/img/rds_instancia.png)

Detalle de la instancia: endpoint, puerto, VPC, subredes y grupo de seguridad asociados.

Bucket S3 creado:

![Bucket creado](Docs/img/s3_bucket.png)

Estructura del bucket app/ y data/:

El bucket contiene dos carpetas principales:

app/ para el paquete de la aplicación
data/ para el archivo de empleados

![Estructura del bucket](Docs/img/s3_bucket_estructura.png)

Paquete de la app subido a S3:

Dentro de la carpeta app/ se encuentra el archivo app_rrhh.zip subido por el script

![app_rrhh.zip en S3](Docs/img/s3_app_carpeta.png)

Archivo empleados.csv subido a S3:

Dentro de la carpeta data/ se encuentra el archivo empleados.csv con los datos generados

![empleados.csv en S3](Docs/img/s3_data_carpeta.png)
----------------------------------------------------------------------
Ubicacion del script en el sistema:

C:\Users\Marco Aurelio\Documents\devops\obligatorio-devops-2025\ejercicio2

-----------------------------------------------------------------------

El script desarrollado cumple con todos los requisitos:

Automatiza el despliegue de una aplicación.

Maneja datos sensibles de forma segura.

Utiliza variables de entorno para credenciales.

Evita exposición de claves en el repositorio.

Lee configuración 100% desde archivo externo.

Puede operar en modo local o modo AWS.

Es totalmente trazable mediante GitHub (commits, ramas, documentación).

-------------------------------------------------------------------------
```python
Codigo ejercicio 2

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
    
# ------------------ Función principal ------------------ #

def main():
    # 1) Leer configuración
    ruta_config = "config_rrhh.env"
    config = leer_config(ruta_config)

    # Config local
    base_dir = config.get("BASE_DIR", "./rrhh_app")
    datos_dir_nombre = config.get("DATOS_DIR", "datos")
    logs_dir_nombre = config.get("LOGS_DIR", "logs")
    nombre_empleados = config.get("ARCHIVO_EMPLEADOS", "empleados.csv")
    nombre_log = config.get("ARCHIVO_LOG", "deploy.log")
    modo_demo = config.get("MODO_DEMO", "SI")

    # Config AWS
    habilitar_aws = config.get("HABILITAR_AWS", "NO").upper() == "SI"
    aws_region = config.get("AWS_REGION", "")
    s3_bucket = config.get("S3_BUCKET", "")
    app_package = config.get("APP_PACKAGE", "app_rrhh.zip")
    s3_app_key = config.get("S3_APP_KEY", "app/app_rrhh.zip")
    s3_empleados_key = config.get("S3_EMPLEADOS_KEY", "data/empleados.csv")
    rds_instancia_id = config.get("RDS_DB_INSTANCE_ID", "rrhh-mysql")
    rds_db_name = config.get("RDS_DB_NAME", "rrhh")
    rds_db_user = config.get("RDS_DB_USER", "admin")

    # 2) Construir rutas locales
    datos_dir = os.path.join(base_dir, datos_dir_nombre)
    logs_dir = os.path.join(base_dir, logs_dir_nombre)
    ruta_empleados = os.path.join(datos_dir, nombre_empleados)
    ruta_log = os.path.join(logs_dir, nombre_log)

    # 3) Crear estructura de directorios
    asegurar_directorio(base_dir)
    asegurar_directorio(datos_dir)
    asegurar_directorio(logs_dir)

    # 4) Registrar inicio en log
    registrar_log(ruta_log, "Inicio de despliegue de aplicación RRHH (local + AWS opcional).")

    # 5) Crear archivo de empleados (demo o vacío)
    cant_registros = crear_archivo_empleados(ruta_empleados, modo_demo)
    registrar_log(
        ruta_log,
        f"Archivo de empleados: {ruta_empleados}. Registros creados (demo): {cant_registros}"
    )

    # 6) Proteger archivo sensible
    proteger_archivo_sensible(ruta_empleados)
    registrar_log(ruta_log, f"Permisos 600 aplicados (si fue posible) sobre {ruta_empleados}")

    # 7) Parte AWS
    if habilitar_aws:
        print("Se habilitó despliegue en AWS según configuración.")
        registrar_log(ruta_log, "Despliegue AWS habilitado.")

        try:
            asegurar_bucket_y_subir(
                aws_region=aws_region,
                bucket_name=s3_bucket,
                app_package_path=app_package,
                s3_app_key=s3_app_key,
                empleados_path=ruta_empleados,
                s3_empleados_key=s3_empleados_key,
                ruta_log=ruta_log,
            )
            asegurar_instancia_rds(
                aws_region=aws_region,
                instancia_id=rds_instancia_id,
                db_name=rds_db_name,
                db_user=rds_db_user,
                ruta_log=ruta_log,
            )
        except Exception as e:
            print(f"Error durante la parte AWS del despliegue: {e}")
            registrar_log(ruta_log, f"ERROR en despliegue AWS: {e}")
        else:
            registrar_log(ruta_log, "Despliegue AWS completado correctamente.")
    else:
        registrar_log(ruta_log, "Despliegue AWS deshabilitado por configuración.")

    # 8) Mensaje final al usuario (sin mostrar salarios)
    print("Despliegue de aplicación RRHH completado (local).")
    print(f"Directorio base: {os.path.abspath(base_dir)}")
    print(f"Archivo de empleados: {os.path.abspath(ruta_empleados)}")
    print(f"Cantidad de registros cargados (demo): {cant_registros}")
    print(f"Log de despliegue: {os.path.abspath(ruta_log)}")
    print("IMPORTANTE: los salarios y datos sensibles NO se muestran por pantalla.")

    registrar_log(ruta_log, "Despliegue local completado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
----------------------------------------------------------------------


