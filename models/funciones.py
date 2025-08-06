import configparser
from models.importaciones import Importaciones
from models.cls_bd import clsBD

class ExecSQLResult:
    def __init__(self, cod_error=0, des_error=''):
        self.cod_error = cod_error
        self.des_error = des_error

class Funciones:
    def fnc_carga_oc(self, desde, hasta):
        result = ExecSQLResult()
        try:
            # 1. Traer importaciones desde SAP (o mock)
            imp = Importaciones()
            inf_import = imp.fnc_importaciones_sap(desde, hasta)
            if inf_import.cod_error != 0:
                raise Exception(f"Error al cargar importaciones desde SAP: {inf_import.des_error}")

            # 2. Abrir conexión SQL Server (desde config.ini)
            config = configparser.ConfigParser()
            config.read('config.ini')
            sqlcfg = config['SQLSERVER']
            bd = clsBD(
                server=sqlcfg['server'],
                database=sqlcfg['database'],
                user=sqlcfg['username'],
                password=sqlcfg['password'],
                driver=sqlcfg.get('driver', "ODBC Driver 18 for SQL Server")
            )
            conn = bd.abrir_bd()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos.")

            with conn:
                cursor = conn.cursor()
                # CABECERA
                for _, row in inf_import.dtZImportaciones_Cab.iterrows():
                    pedido = row["EBELN"].strip()
                    cursor.execute("SELECT 1 FROM ROS_IMPORTACIONES_CAB WHERE NROPEDIDO = ?", pedido)
                    if cursor.fetchone() is None:
                        sql_insert = """
                        INSERT INTO ROS_IMPORTACIONES_CAB (
                            NROPEDIDO, CAMPO2, MONTO, DENOMINACION, FECHAPEDIDO, WAERS, RLWRT,
                            FLIBERACION, WKURS, EKORG, ZZPTOEMBA, ERNAM
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        valores = [
                            pedido,
                            pedido[-5:],
                            0,
                            self.retorna_origen(row.get('DENOMINACION', '').upper().strip()),
                            self.formatea_fecha(row["BEDAT"]),
                            row.get('WAERS', '').strip(),
                            float(row.get('RLWRT', 0)),
                            self.formatea_fecha(row.get("FLIBERACION")),
                            float(row.get('WKURS', 0)),
                            row.get('EKORG', '').strip(),
                            row.get('ZZPTOEMBA', '').strip(),
                            row.get('ERNAM', '').strip()
                        ]
                        cursor.execute(sql_insert, valores)
                    elif self.is_date(row.get('FLIBERACION', "")):
                        sql_update = """
                        UPDATE ROS_IMPORTACIONES_CAB
                        SET FLIBERACION = ?, ORIGEN = ?, MONTO_NETO = ?
                        WHERE NROPEDIDO = ?
                        """
                        cursor.execute(
                            sql_update,
                            self.formatea_fecha(row["FLIBERACION"]),
                            self.retorna_origen(row.get('DENOMINACION', '').upper().strip()),
                            float(row.get("RLWRT", 0)),
                            pedido
                        )
                # DETALLE
                for _, row in inf_import.dtZImportaciones_Det.iterrows():
                    pedido, posicion = row["EBELN"].strip(), row["EBELP"]
                    cursor.execute(
                        "SELECT 1 FROM ROS_IMPORTACIONES_DET WHERE NROPEDIDO = ? AND POSICION = ?",
                        (pedido, posicion))
                    if cursor.fetchone():
                        cursor.execute(
                            "DELETE FROM ROS_IMPORTACIONES_DET WHERE NROPEDIDO = ? AND POSICION = ?",
                            (pedido, posicion))
                    sql_insert_det = """
                        INSERT INTO ROS_IMPORTACIONES_DET (
                            NROPEDIDO, POSICION, TXZ01, MATNR, MAKTX, WERKS, LGORT, MENGE, MEINS, NETPR, NETWR
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    valores_det = [
                        pedido,
                        posicion,
                        row.get('TXZ01', '').replace("'", "''").strip(),
                        row.get('MATNR', '').strip(),
                        row.get('MAKTX', '').replace("'", "''").strip(),
                        row.get('WERKS', '').strip(),
                        row.get('LGORT', '').strip(),
                        float(row.get('MENGE', 0)),
                        row.get('MEINS', '').strip(),
                        float(row.get('NETPR', 0)),
                        float(row.get('NETWR', 0)),
                    ]
                    cursor.execute(sql_insert_det, valores_det)
                conn.commit()

        except Exception as ex:
            if 'conn' in locals() and conn:
                conn.rollback()
            result.cod_error = 1
            result.des_error = str(ex)
        finally:
            if 'bd' in locals():
                bd.cerrar_bd()
        return result

    @staticmethod
    def formatea_fecha(yyyymmdd):
        import pandas as pd
        try:
            return pd.to_datetime(yyyymmdd, format='%Y%m%d').date()
        except Exception:
            return None

    @staticmethod
    def is_date(yyyymmdd):
        import pandas as pd
        try:
            pd.to_datetime(yyyymmdd, format='%Y%m%d', errors='raise')
            return True
        except Exception:
            return False

    @staticmethod
    def retorna_origen(origen: str) -> str:
        import unicodedata
        sb = []
        if "Ñ" in origen or "ñ" in origen:
            for ch in origen.strip():
                uc = unicodedata.category(ch)
                if uc not in ("Mn", "Po"):
                    sb.append(ch)
        else:
            st_form_d = unicodedata.normalize('NFD', origen)
            for ch in st_form_d:
                uc = unicodedata.category(ch)
                if uc not in ("Mn", "Po"):
                    sb.append(ch)
        return unicodedata.normalize('NFC', ''.join(sb))
