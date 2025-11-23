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