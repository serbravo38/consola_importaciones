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
            # 1. Traer importaciones desde SAP
            imp = Importaciones()
            inf_import = imp.fnc_importaciones_sap(desde, hasta)
            if inf_import.cod_error != 0:
                raise Exception(f"Error al cargar importaciones desde SAP: {inf_import.des_error}")

            # 2. Abrir conexión Oracle (desde config.ini)
            config = configparser.ConfigParser()
            config.read('config.ini')
            ora_cfg = config['ORACLE']
            bd = clsBD(
                user=ora_cfg['user'],
                password=ora_cfg['password'],
                dsn=ora_cfg['dsn']
            )
            conn = bd.abrir_bd()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos.")

            with conn:
                cursor = conn.cursor()
                # CABECERA
                for _, row in inf_import.dtZImportaciones_Cab.iterrows():
                    pedido = row["EBELN"].strip()
                    cursor.execute("SELECT 1 FROM ROS_IMPORTACIONES_CAB WHERE NROPEDIDO = :pedido", {"pedido": pedido})
                    if cursor.fetchone() is None:
                        # IMPORTANTE: verificar los campos en la tabla ROS_IMPORTACIONES_CAB
                        sql_insert = """
                        INSERT INTO ROS_IMPORTACIONES_CAB (
                            NROPEDIDO, CAMPO2, MONTO, DENOMINACION, FECHAPEDIDO, WAERS, RLWRT,
                            FLIBERACION, WKURS, EKORG, ZZPTOEMBA, ERNAM
                        ) VALUES (
                            :pedido, :campo2, :monto, :denominacion, :fechapedido, :waers, :rlwrt,
                            :fliberacion, :wkurs, :ekorg, :zptoemba, :ernam
                        )
                        """
                        valores = {
                            "pedido": pedido,
                            "campo2": pedido[-5:],
                            "monto": 0,
                            "denominacion": self.retorna_origen(row.get('DENOMINACION', '').upper().strip()),
                            "fechapedido": self.formatea_fecha(row["BEDAT"]),
                            "waers": row.get('WAERS', '').strip(),
                            "rlwrt": float(row.get('RLWRT', 0)),
                            "fliberacion": self.formatea_fecha(row.get("FLIBERACION")),
                            "wkurs": float(row.get('WKURS', 0)),
                            "ekorg": row.get('EKORG', '').strip(),
                            "zptoemba": row.get('ZZPTOEMBA', '').strip(),
                            "ernam": row.get('ERNAM', '').strip()
                        }
                        cursor.execute(sql_insert, valores)
                    elif self.is_date(row.get('FLIBERACION', "")):
                        sql_update = """
                        UPDATE ROS_IMPORTACIONES_CAB
                           SET FLIBERACION = :fliberacion,
                               ORIGEN = :origen,
                               MONTO_NETO = :monto
                         WHERE NROPEDIDO = :pedido
                        """
                        cursor.execute(
                            sql_update,
                            {
                                "fliberacion": self.formatea_fecha(row["FLIBERACION"]),
                                "origen": self.retorna_origen(row.get('DENOMINACION', '').upper().strip()),
                                "monto": float(row.get("RLWRT", 0)),
                                "pedido": pedido
                            }
                        )
                # DETALLE
                for _, row in inf_import.dtZImportaciones_Det.iterrows():
                    pedido, posicion = row["EBELN"].strip(), row["EBELP"]
                    cursor.execute(
                        "SELECT 1 FROM ROS_IMPORTACIONES_DET WHERE NROPEDIDO = :pedido AND POSICION = :posicion",
                        {"pedido": pedido, "posicion": posicion}
                    )
                    if cursor.fetchone():
                        cursor.execute(
                            "DELETE FROM ROS_IMPORTACIONES_DET WHERE NROPEDIDO = :pedido AND POSICION = :posicion",
                            {"pedido": pedido, "posicion": posicion}
                        )
                    sql_insert_det = """
                        INSERT INTO ROS_IMPORTACIONES_DET (
                            NROPEDIDO, POSICION, TXZ01, MATNR, MAKTX, WERKS, LGORT, MENGE, MEINS, NETPR, NETWR
                        ) VALUES (
                            :pedido, :posicion, :txz01, :matnr, :maktx, :werks, :lgort, :menge, :meins, :netpr, :netwr
                        )
                    """
                    valores_det = {
                        "pedido": pedido,
                        "posicion": posicion,
                        "txz01": row.get('TXZ01', '').replace("'", "''").strip(),
                        "matnr": row.get('MATNR', '').strip(),
                        "maktx": row.get('MAKTX', '').replace("'", "''").strip(),
                        "werks": row.get('WERKS', '').strip(),
                        "lgort": row.get('LGORT', '').strip(),
                        "menge": float(row.get('MENGE', 0)),
                        "meins": row.get('MEINS', '').strip(),
                        "netpr": float(row.get('NETPR', 0)),
                        "netwr": float(row.get('NETWR', 0)),
                    }
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
