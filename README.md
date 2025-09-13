# Hackeo de cámaras Hikvision en Android usando Termux
​Esta guía te proporcionará los pasos detallados para instalar y ejecutar el script en tu dispositivo Android utilizando la aplicación Termux.
### ​Paso 1: Instalación de Termux
# ​⚠️ ¡Importante! No descargues Termux desde la Google Play Store, ya que la versión allí está desactualizada y no es compatible con las herramientas modernas.
​Descarga Termux desde una fuente confiable:
​F-Droid (recomendado): Visita el sitio web de [F-Droid](https://f-droid.org/en/packages/com.termux/?hl=es-US) o descarga su aplicación para instalar Termux de forma segura y actualizada.

GitHub: Descarga el archivo APK más reciente directamente del [repositorio oficial de Termux en GitHub](https://github.com/termux/termux-app/releases/tag/v0.118.3).
### Paso 2: Preparación del Entorno en Termux
​Una vez que tengas Termux instalado, abre la aplicación y ejecuta los siguientes comandos en el orden indicado para configurar tu entorno.
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
