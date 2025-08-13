import configparser
import os
from models.cls_bd import clsBD
import oracledb

# Inicializa el cliente de Oracle. Solo es necesario hacerlo una vez al inicio.
oracledb.init_oracle_client(lib_dir=r"C:\instantclient_23_8")  # Ajusta si tu ruta es otra


def test_conexion():
    
    raiz_proyecto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')  # subir un nivel si el script está en una carpeta dentro
    )

    # Si el script ya está en la raíz, sobrescribimos
    if os.path.basename(raiz_proyecto).lower() != "consola_importaciones":
        # Buscar la carpeta Consola_importaciones dentro de la ruta actual
        posible_ruta = os.path.join(os.path.expanduser("~"), "Desktop", "Consola_importaciones")
        if os.path.isdir(posible_ruta):
            raiz_proyecto = posible_ruta

    # Armar ruta final del archivo
    config_path = os.path.join(raiz_proyecto, 'config.init')

    # Depuración para confirmar ruta
    print(f"📂 Raíz del proyecto: {raiz_proyecto}")
    print(f"📄 Ruta completa a config.init: {config_path}")

    if not os.path.isfile(config_path):
        print(f"❌ Archivo de configuración no encontrado en: {config_path}")
        return

    # Leer configuración
    config = configparser.ConfigParser()
    config.read(config_path)

    if 'ORACLE' not in config:
        print("❌ No se encontró la sección [ORACLE] en config.init")
        print(f"Secciones encontradas: {config.sections()}")
        return

    ora_cfg = config['ORACLE']

    # Crear instancia de la conexión
    bd = clsBD(
        user=ora_cfg.get('user', ''),
        password=ora_cfg.get('password', ''),
        dsn=ora_cfg.get('dsn', '')
    )

    conn = bd.abrir_bd()
    if conn:
        print("✅ Conexión a Oracle exitosa")
        try:
            df = bd.ejecutar("SELECT SYSDATE AS FECHA_ACTUAL FROM dual")
            print(df)
        except Exception as e:
            print(f"❌ Error ejecutando query: {e}")
        finally:
            bd.cerrar_bd()
    else:
        print("❌ No se pudo establecer la conexión a Oracle")


if __name__ == "__main__":
    test_conexion()
