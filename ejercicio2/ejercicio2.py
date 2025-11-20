#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime


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
