import pandas as pd

class InfImportaciones:
    def __init__(self):
        self.dtZImportaciones_Det = pd.DataFrame()
        self.dtZImportaciones_Cab = pd.DataFrame()
        self.cod_error = 0
        self.des_error = ''
