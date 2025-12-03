Este archivo contiene la solución completa del Obligatorio de Programación para DevOps 2025, compuesto por:

Ejercicio 1 (Bash):
Script que automatiza la creación de usuarios en Linux a partir de un archivo de entrada, aplicando verificaciones, manejo de errores y opciones adicionales de ejecución.

Incluye:
-	Shell por defecto. 
-	Directorio home. 
-	Comentario asociado al usuario. 
-	Opción para crear el directorio home si no existe. 
-	Además, incluye opciones para: 
-	Informar el resultado de la creación de cada usuario. 
-	Asignar una contraseña común a todos los usuarios. 

Ejercicio 2 (Python + AWS)

Automatización del despliegue completo de una aplicación de Recursos Humanos en AWS, asegurando la correcta gestión de datos sensibles.

Incluye:
-	Preparación del entorno local y archivos de la aplicación.
-	Subida del contenido web a un bucket S3.
-	Creación de Security Groups para aislar la capa web y la base de datos.
-	Aprovisionamiento de una instancia MySQL en AWS RDS con cifrado y backups.
-	Lanzamiento de una instancia EC2 con instalación automática de Apache y PHP.
-	Sincronización de archivos desde S3, configuración del archivo .env y carga    opcional del script SQL inicial.
-	Protección de credenciales mediante inputs y permisos seguros en la instancia.


Estructura del repositorio:

```bash

obligatorio-devops-2025/
├── ejercicio1/
│   ├── Docs/
│   │   ├── Salida_ejecucion.png
│   │   └── salida_ejecucion_ambos_modificadores.png
│   ├── ej1_crea_usuarios.sh
│   └── usuarios.txt
│
├── ejercicio2/
│   ├── ejercicio2.py
│   └── ArchivosWeb/
│
├── .gitignore
└── README.md

     
```

Link del repositorio: https://github.com/marcodm104/obligatorio-devops-2025

Gestión del repositorio y uso de ramas:

main: rama principal con la versión final y estable del proyecto

ej2-python: usada para desarrollar y probar el Ejercicio 2 sin afectar la rama principal.

documentacion: destinada a la elaboración del README, incorporación de imágenes y ajustes finales.

Cada rama se desarrolló de forma independiente y, una vez que los cambios estaban completos, se integraron en main mediante merges directos, resolviendo los conflictos que surgieron durante el proceso.
Este flujo permitió trabajar de forma ordenada y mantener control sobre cada parte del proyecto.

Cuando todos los cambios quedaron unificados y verificados, las ramas de trabajo fueron eliminadas para dejar el repositorio limpio y con una única versión final.
El historial de commits y merges permanece disponible como evidencia del proceso de desarrollo y del uso de buenas prácticas de control de versiones.

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

| Código | Motivo     | Descripción                                |
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

Prueba con modificador -i:

![Salida real del script](ejercicio1/Docs/Salida_ejecucion.png)

Prueba utilizando ambos modificadores y asignando contraseña (-i y -c)

![Salida real del script](ejercicio1/Docs/salida_ejecucion_ambos_modificadores.png)

---------------------------------------------------------------------------------


Requisitos / Dependencias

Para que el script pueda ejecutarse sin problemas, es necesario contar con un entorno previamente configurado tanto a nivel local como en la plataforma de AWS.
En el equipo donde se ejecute el programa se debe disponer de Python 3 y de las librerías necesarias para interactuar con los servicios de la nube. En particular, se utilizan los módulos boto3 y botocore, que permiten crear, administrar y consultar recursos de AWS directamente desde el código. Ambos paquetes pueden instalarse mediante:

pip install boto3 botocore

Además del entorno de Python, se requiere que la AWS CLI esté instalada y correctamente configurada con un usuario que cuente con permisos suficientes para aprovisionar infraestructura. Las credenciales asociadas deben habilitar acciones sobre los servicios utilizados en el despliegue, tales como Amazon S3, EC2 y RDS. Sin estas políticas, el script no podrá crear ni modificar los recursos necesarios.

También es indispensable contar con la carpeta local que contiene los archivos de la aplicación web, la cual el script sincroniza automáticamente hacia el bucket de S3. Dichos archivos deben ubicarse dentro del directorio ArchivosWeb, manteniendo la estructura prevista para que el servidor web pueda procesarlos correctamente.

En conjunto, estas dependencias, tanto de software como de configuración en AWS garantizan que el script pueda ejecutar todas las etapas del despliegue de forma segura, automatizada y sin errores.

------------------------------------------------------------------------
Funcionalidad y medidas de seguridad

El script desarrollado en Python tiene como finalidad automatizar todo el proceso de despliegue de la aplicación de Recursos Humanos dentro de la infraestructura de AWS. Para lograrlo, se emplea la librería boto3, que permite crear y configurar servicios en la nube siguiendo principios de Infraestructura como Código, garantizando un despliegue repetible, ordenado y seguro.

El proceso comienza con la preparación del contenido web: el script verifica la existencia de la carpeta local de la aplicación y carga todos los archivos necesarios en un bucket de Amazon S3. Esto permite que la instancia EC2, que se aprovisionará más adelante, pueda descargar y ejecutar la aplicación sin intervención manual.

Luego, el script crea los grupos de seguridad que definen el flujo de tráfico dentro del entorno. Por un lado, se configura un Security Group para la capa web, permitiendo únicamente tráfico HTTP desde cualquier origen. Por otro, se genera un Security Group específico para la base de datos, el cual restringe completamente las conexiones externas y solo admite solicitudes provenientes del servidor web. Esta separación entre capas reduce significativamente la superficie de ataque y asegura un aislamiento adecuado entre servicios.

A continuación, se provisiona una base de datos MySQL mediante Amazon RDS. La instancia es creada con almacenamiento cifrado, backups automáticos habilitados y parámetros que refuerzan la seguridad, cumpliendo con los requisitos de protección de datos sensibles. El endpoint de la base de datos se obtiene dinámicamente una vez que el servicio está disponible, lo que permite integrarlo automáticamente con la instancia EC2.

Durante el lanzamiento de la instancia EC2, el script genera un User Data personalizado que se ejecuta al iniciar el servidor. Este User Data instala Apache, PHP y los complementos requeridos, descarga los archivos de la aplicación desde S3, configura los permisos adecuados, genera el archivo .env con las credenciales necesarias y ejecuta el script SQL init_db.sql si está presente. Todo este proceso asegura que la aplicación quede completamente funcional al terminar el aprovisionamiento.

A diferencia de otras implementaciones que almacenan credenciales en archivos externos, este script solicita la contraseña directamente al usuario mediante un input interactivo, evitando que quede en el repositorio o en el sistema de archivos. Esto reduce el riesgo de exposición accidental y elimina la necesidad de manejar archivos sensibles.

Además, las credenciales se escriben únicamente dentro del archivo .env en la instancia EC2, el cual se genera con permisos estrictos (600) para impedir su lectura por parte de otros usuarios del sistema.
---------------------------------------------------------------------
Modo de uso y ejemplo de ejecucion

Para ejecutar el script hay que ubicarse en el directorio donde se encuentra el archivo del ejercicio y ejecutar en la terminal:

Python ej2.py

![Ejemplo ejecucion script](ejercicio2/ejemplo-ejecucion.jpeg)

Una vez ejecutado hay que asignar un nombre para el bucket (Tiene que ser unico) y luego escribir una contraseña para la base de datos.

Al comenzar, el script va mostrando en pantalla el avance de cada una de las etapas del despliegue. Inicialmente se encarga de verificar y cargar los archivos de la aplicación en el bucket de S3, indicando si el bucket ya existía o si fue creado durante la ejecución.

Luego continúa con la creación de los Security Groups correspondientes a la capa web y a la base de datos. Una vez configurada la red, el script procede a desplegar la instancia RDS y mantiene informado al usuario durante el tiempo de espera hasta que quede completamente operativa.

Con la base de datos disponible, se inicia el aprovisionamiento de la instancia EC2. Tras unos segundos adicionales para permitir la inicialización completa, el script obtiene la dirección IP pública de la instancia.
Finalmente, se imprime en pantalla la URL de acceso a la aplicación, confirmando que todos los recursos fueron creados y configurados correctamente.
 
Una vez obtenida la URL de la app, se pega en un navegador y se ingresa al login.php. Luego, ingresamos con usuario y contraseña y accedemos a la app.
Una vez realizado el login, ya tendríamos acceso a la web (En este ejemplo ip 18.209.22.62)

![Despliegue de app](ejercicio2/app-desplegada.jpeg)

Para corroborar el funcionamiento se eliminaron usuarios y se creó uno nuevo.
 
----------------------------------------------------------------------


