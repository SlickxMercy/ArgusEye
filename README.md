# Hackeo de cámaras Hikvision en Android usando Termux
​Esta guía te proporcionará los pasos detallados para instalar y ejecutar el script en tu dispositivo Android utilizando la aplicación Termux.
### ​Paso 1: Instalación de Termux
# ​⚠️ ¡Importante! No descargues Termux desde la Google Play Store, ya que la versión allí está desactualizada y no es compatible con las herramientas modernas.
​Descarga Termux desde una fuente confiable:
​F-Droid (recomendado): Visita el sitio web de [F-Droid](https://f-droid.org/en/packages/com.termux/?hl=es-US) o descarga su aplicación para instalar Termux de forma segura y actualizada.

GitHub: Descarga el archivo APK más reciente directamente del [repositorio oficial de Termux en GitHub](https://github.com/termux/termux-app/releases/tag/v0.118.3).
### Paso 2: Preparación del Entorno en Termux
​Una vez que tengas Termux instalado, abre la aplicación y ejecuta los siguientes comandos en el orden indicado para configurar tu entorno.
### Paso 3 instalas librerias
```bash
termux-setup-storag
```
Cuando se te pida, concede los permisos de almacenamiento a Termux. Esto es necesario para que el script pueda guardar los archivos de resultados.

```bash
pkg update && pkg upgrade -y
```
```bash
pkg install python git -y
```
```bash
pip install requests colorama loguru passlib lxml pycryptodome urllib3
```

```bash
cd storage/downloads/
```
```bash
git clone https://github.com/SlickxMercy/ArgusEye
```
```bash
cd ArgusEye
```
```bash
python ArgusEye
```
### Paso 4: Funcionalidades del Menú
# El script te guiará a través de un menú intuitivo. Aquí tienes un desglose de cada opción:
# ​Scanner (Escaneo de Rango CIDR): 
Utiliza esta opción para escanear un rango de IP (por ejemplo, 192.168.1.0/24) y encontrar hosts activos con el puerto 80 abierto. Los hosts encontrados se guardarán automáticamente en un archivo llamado host.txt.
# ​Brute Force (Hikvision):
Este módulo realiza un ataque de fuerza bruta a las direcciones IP listadas en host.txt utilizando diccionarios de usuarios (user.txt) y contraseñas (pass.txt) predefinidos.
# ​CVE-2017-7921 (Hikvision): 
Explota esta vulnerabilidad de divulgación de información para obtener credenciales de administrador de forma automática.
# Uniview Disclosure: 
Intenta explotar una vulnerabilidad en cámaras Uniview para obtener sus credenciales. 
# CVE-2021-36260 (Hikvision): 
Este módulo comprueba la existencia de la vulnerabilidad de inyección de comandos. Si una cámara es vulnerable, el script puede instalar una puerta trasera (backdoor) SSH para acceso futuro.
# ​Exit: 
Sal del script.
### Consejos Adicionales

(algunos códigos no estan funcionando correctamente como la vulnerabilidad cve-2021-36260)


​Detener la ejecución: Para detener el script en cualquier momento, presiona Ctrl + C.
​Actualización de diccionarios: Asegúrate de que los archivos user.txt y pass.txt contengan listas de usuarios y contraseñas que deseas probar. Puedes editarlos con un editor de texto simple.
​Conexión a Internet: Para que el script funcione correctamente, tu dispositivo Android debe tener una conexión a Internet activa.
​Organización: El script crea una carpeta de output para guardar los resultados, incluyendo las cámaras vulnerables y las capturas de pantalla (snapshots). Revisa estos directorios para ver el progreso y los hallazgos del escaneo.
### ​¡Recuerda utilizar esta herramienta de forma ética y legal!
