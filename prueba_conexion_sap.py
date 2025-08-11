import configparser
from pyrfc import Connection

def test_conexion_sap():
    try:
        # Leer datos de SAP desde config.init
        config = configparser.ConfigParser()
        config.read('config.init')

        sap_cfg = config['SAP']
        conn_params = {
            "ashost": sap_cfg['ashost'],
            "sysnr": sap_cfg['sysnr'],
            "client": sap_cfg['client'],
            "user": sap_cfg['user'],
            "passwd": sap_cfg['passwd'],
            "lang": sap_cfg.get('lang', 'ES')
        }

        # Conectar a SAP
        connection = Connection(**conn_params)
        print("✅ Conexión a SAP establecida con éxito.")

        # Ejemplo de llamada: obtener detalles del usuario SAP
        result = connection.call("BAPI_USER_GET_DETAIL", USERNAME=sap_cfg['user'])

        print("\n📌 Detalles del usuario SAP:")
        print(f"Nombre de usuario: {result.get('USERNAME', '')}")
        print(f"Nombre completo: {result.get('FULLNAME', '')}")

        # Cierre de conexión
        connection.close()
        print("\n🔒 Conexión a SAP cerrada.")

    except Exception as e:
        print(f"❌ Error al conectar a SAP: {e}")

if __name__ == "__main__":
    test_conexion_sap()
