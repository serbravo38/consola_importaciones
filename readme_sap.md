Guía: Conectar SAP desde Visual Studio Code con Python
1. Requisitos previos
Antes de comenzar, debes tener:

Visual Studio Code instalado.

Python 3.8 o superior instalado y configurado en tu PC.

Credenciales SAP:

Usuario

Contraseña

Host / IP del servidor SAP

Número de sistema (sysnr)

Cliente (client)

Idioma (lang)

SAP NetWeaver RFC SDK descargado desde el portal oficial de SAP (requiere cuenta SAP).

2. Instalar SAP NetWeaver RFC SDK
Descarga el SDK desde el SAP Support Portal:
https://support.sap.com → Buscar "SAP NetWeaver RFC SDK".

Extrae el contenido en una carpeta, por ejemplo:

makefile
Copiar
Editar
C:\nwrfcsdk
Asegúrate de que las carpetas lib y include estén dentro de esa ruta.

3. Configurar variables de entorno
Debes indicar a tu sistema dónde está el SDK:

En Windows:
Abre Panel de Control → Sistema → Configuración avanzada del sistema → Variables de entorno.

En Variables del sistema añade:

ini
Copiar
Editar
RFC_SDK = C:\nwrfcsdk
PATH = C:\nwrfcsdk\lib; %PATH%
Guarda y reinicia la terminal.

En Linux/macOS:
En tu .bashrc o .zshrc:

bash
Copiar
Editar
export SAPNWRFC_HOME=/usr/local/nwrfcsdk
export PATH=$SAPNWRFC_HOME/lib:$PATH
4. Crear un entorno virtual en Python
En Visual Studio Code, abre la carpeta de tu proyecto y crea un entorno virtual:

bash
Copiar
Editar
python -m venv venv
Activar:

Windows:

bash
Copiar
Editar
venv\Scripts\activate
Linux/macOS:

bash
Copiar
Editar
source venv/bin/activate
5. Instalar PyRFC
Con el entorno virtual activo:

bash
Copiar
Editar
pip install pyrfc
Nota: Si da error, es porque el SDK no está correctamente configurado o el compilador no encuentra las librerías.

6. Crear el script de conexión
Crea un archivo sap_connect.py:

python
Copiar
Editar
from pyrfc import Connection

# Configuración de conexión
conn_params = {
    'user': 'USUARIO_SAP',
    'passwd': 'CONTRASEÑA',
    'ashost': 'IP_O_HOST',
    'sysnr': '00',        # Número de sistema SAP
    'client': '100',      # Cliente SAP
    'lang': 'ES'          # Idioma
}

try:
    # Conexión a SAP
    conn = Connection(**conn_params)
    print("✅ Conexión exitosa a SAP")

    # Ejemplo: llamar una función RFC de SAP
    result = conn.call('STFC_CONNECTION')
    print("Resultado:", result)

except Exception as e:
    print("❌ Error de conexión:", e)
7. Ejecutar desde Visual Studio Code
En la terminal de VS Code:

bash
Copiar
Editar
python sap_connect.py
Si todo está bien, verás:

bash
Copiar
Editar
✅ Conexión exitosa a SAP
Resultado: {'ECHOTEXT': '...', 'RESPTEXT': 'SAP R/3 connection test OK', ...}
8. Buenas prácticas
No guardes usuario y contraseña en el código; usa un .env y python-dotenv.

Maneja errores con try/except.

Si usarás muchas llamadas RFC, implementa reconexiones automáticas.
