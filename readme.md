pip install oracledb pandas
 Si tu sistema no tiene el Oracle Instant Client, descárgalo de oracle.com, descomprime y agrega la ruta al PATH del sistema. En algunos sistemas Linux será necesario instalar también paquetes de desarrollo de Oracle.
 Instant Client Setup: Si ves errores como “DPI-1047: Cannot locate a 64-bit Oracle Client library”, descarga y configura el Instant Client en el PATH.
Instalar los siguientes paquetes
pip install pandas oracledb boto3 pyrfc

pyrfc: Solo si vas a conectar a SAP real (requiere tener el SAP NWRFC SDK instalado además del paquete).
pip install pyrfc

# Guía para conectar SAP a Python

## 1. Requisitos previos

Antes de comenzar, necesitas tener lo siguiente:

* **Python:** Asegúrate de tener Python 3.x instalado en tu sistema.
* **SAP NWRFC SDK:** Esta es la biblioteca oficial de SAP. Debes descargarla desde el [SAP Support Portal](https://support.sap.com/en/product/connectors/nwrfcsdk.html). Necesitas una cuenta S-User para acceder. Descarga la versión adecuada para tu sistema operativo y arquitectura.
* **Credenciales de SAP:** Necesitarás tu **nombre de usuario**, **contraseña**, **ID del cliente**, **idioma** y la información del servidor (**host** y **número de sistema**).

---

## 2. Instalación y configuración

1.  **Instala la librería `pyrfc`** a través de pip en tu terminal o línea de comandos:

    ```bash
    pip install pyrfc
    ```

2.  **Configura el SAP NWRFC SDK:** Descomprime el SDK que descargaste y asegúrate de que las librerías compartidas (archivos `.dll`, `.so`, o `.dylib`) sean accesibles para tu sistema. La forma más sencilla es agregar la ruta al directorio `lib` del SDK a tu variable de entorno `PATH`.
    * **En Windows:** Edita la variable `PATH` en "Variables de entorno" para agregar la ruta del directorio `lib` del SDK.
    * **En Linux/macOS:** Agrega la ruta a tu `~/.bashrc` o `~/.zshrc` con `export LD_LIBRARY_PATH=/ruta/al/sdk/lib:$LD_LIBRARY_PATH` (Linux) o `export DYLD_LIBRARY_PATH=/ruta/al/sdk/lib:$DYLD_LIBRARY_PATH` (macOS).

---

## 3. Código de ejemplo para la conexión

Una vez que tengas todo configurado, puedes escribir un script de Python para conectarte a SAP.

1.  **Crea un archivo de Python** (por ejemplo, `sap_connection.py`).
2.  **Copia y pega el siguiente código**, reemplazando los datos de ejemplo con tus propias credenciales de SAP.

    ```python
    from pyrfc import Connection

    try:
        # Define los parámetros de conexión
        conn_params = {
            "ashost": "tu_host_sap",
            "sysnr": "tu_numero_de_sistema",
            "client": "tu_cliente_sap",
            "user": "tu_usuario_sap",
            "passwd": "tu_contraseña_sap",
            "lang": "ES"
        }

        # Establece la conexión
        connection = Connection(**conn_params)
        print("Conexión a SAP establecida con éxito.")

        # Ejemplo de llamada a una función BAPI o RFC de SAP
        # En este caso, obtiene detalles del usuario actual
        result = connection.call("BAPI_USER_GET_DETAIL", USERNAME="tu_usuario_sap")
        print("\nDetalles del usuario:")
        print(f"Nombre de usuario: {result['USERNAME']}")
        print(f"Nombre completo: {result['FULLNAME']}")

        # Cierra la conexión al finalizar
        connection.close()
        print("\nConexión a SAP cerrada.")

    except Exception as e:
        print(f"Error al conectar a SAP: {e}")
    ```

---

## 4. Ejecutar el script

Guarda el archivo y ejecútalo desde tu terminal:

```bash
python sap_connection.py