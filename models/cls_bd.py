import pyodbc
import pandas as pd

class clsBD:
    def __init__(self, server, database, user, password, driver="ODBC Driver 18 for SQL Server"):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.driver = driver
        self.connection = None

    def abrir_bd(self):
        try:
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;"
            )
            self.connection = pyodbc.connect(conn_str)
            return self.connection
        except Exception as e:
            print(f"Error al conectar a SQL Server: {e}")
            return None

    def cerrar_bd(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def ejecutar(self, sql, params=None):
        if not self.connection:
            raise Exception("No hay conexión abierta")
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params or [])
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
