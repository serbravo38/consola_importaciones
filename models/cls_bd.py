import oracledb
import pandas as pd

class clsBD:
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.connection = None

    def abrir_bd(self):
        try:
            self.connection = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
            return self.connection
        except Exception as e:
            print(f"Error al conectar a la BD Oracle: {e}")
            return None

    def cerrar_bd(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def ejecutar(self, sql, params=None):
        if not self.connection:
            raise Exception("No hay conexión abierta")
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            try:
                cols = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=cols)
            except Exception:
                self.connection.commit()
                return None

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()
