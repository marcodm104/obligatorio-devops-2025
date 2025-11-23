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

obligatorio-devops-2025/
│
├── ejercicio1/
│   ├── ej1_crea_usuarios.sh
│   └── usuarios.txt
│
├── ejercicio2/
│   ├── ejercicio2.py
│   ├── config_rrhh.env
│   ├── empleados.csv
│   ├── app.py
│   ├── app_rrhh.zip
│
├── .gitignore
└── README.md        

Link del repositorio: https://github.com/marcodm104/obligatorio-devops-2025

Requisitos / Dependencias

Ejercicio 1 (Bash)

Debe ejecutarse en un entorno Linux con:
- bash 4.x o superior
- permisos para crear usuarios
- archivo de entrada con formato: nombre:comentario:/home/directorio:SI|NO

---------------------------------------------------------------------------
Requisitos / Dependencias

Ejercicio 2 (Python + AWS)
Requiere:
- Python 3.8+
- Librerías instaladas:
boto3
botocore

Instalación:

pip install boto3 botocore

Archivo de configuración config_rrhh.env

cuenta AWS Academy con permisos sobre S3 y RDS.

Variable de entorno obligatoria para AWS RDS:

export RDS_ADMIN_PASSWORD="ContraseñaComplicada123!"

----------------------------------------------------------------
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

Código	Motivo	    Descripción
10	    Parámetros	Cantidad incorrecta de parámetros
11	    Parámetros	Falta contraseña tras -c
12	    Parámetros	Modificador inválido
13	    Archivo	    No se proporcionó archivo de entrada
20	    Archivo	    El archivo no existe
21	    Archivo	    El archivo no es regular
22	    Archivo	    Sin permisos de lectura
30	    Formato	    Cantidad incorrecta de campos
31	    Formato	    Campo "SI/NO" inválido
------------------------------------------------------------------------

Ubicacion del script en el sistema:

C:\Users\Marco Aurelio\Documents\devops\obligatorio-devops-2025\ejercicio1

------------------------------------------------------------------------

Ejemplo salida real de la ejecución.

El script fue probado en una máquina virtual Centos 8.1, verificando su correcto funcionamiento.

![Salida real del script](ejercicio1/Salida_ejecucion.png)

El script cumple con todos los requisitos solicitados: creación de usuarios, validación de parámetros, manejo de errores, modularidad y evidencia real de ejecución.
La ejecución fue probada en un entorno Linux real, y los usuarios fueron creados correctamente siguiendo el formato establecido.
------------------------------------------------------------------------
