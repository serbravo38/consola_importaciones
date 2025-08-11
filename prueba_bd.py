import configparser
from models.cls_bd import clsBD

def test_conexion():
    # Leer datos del config.ini
    config = configparser.ConfigParser()
    config.read('config.init')
    

    ora_cfg = config['ORACLE']  

    # Crear instancia de conexión
    bd = clsBD(
        user=ora_cfg['user'],
        password=ora_cfg['password'],
        dsn=ora_cfg['dsn']
    )

    conn = bd.abrir_bd()
    if conn:
        print("✅ Conexión a Oracle exitosa")
        try:
            # Consulta simple para validar
            df = bd.ejecutar("SELECT SYSDATE AS FECHA_ACTUAL FROM dual")
            print(df)
        except Exception as e:
            print(f"❌ Error ejecutando query de prueba: {e}")
        finally:
            bd.cerrar_bd()
    else:
        print("❌ No se pudo establecer la conexión a Oracle")

if __name__ == "__main__":
    test_conexion()
