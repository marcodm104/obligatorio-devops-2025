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
│   └── datos/ y logs/ (generadas por el script)
│
├── .gitignore
└── README.md        # Este documento

Link del repositorio: https://github.com/marcodm104/obligatorio-devops-2025


