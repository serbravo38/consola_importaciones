import pandas as pd
import configparser
from pyrfc import Connection  # Instalar paquete pip pyrfc  y el SDK SAP configurado
from models.inf_importaciones import InfImportaciones

class Importaciones:
    def __init__(self):
        self.dbc_SAP = None

    def fnc_importaciones_sap(self, desde: str, hasta: str):
        cls_inf_importaciones = InfImportaciones()
        bol_cierra = False

        try:
            if self.dbc_SAP is None:
                self.dbc_SAP = self.abrir_sap()
                bol_cierra = True

            # Llama a la función RFC ZIMPORTACIONES con los parámetros requeridos
            rfc_response = self.dbc_SAP.call(
                'ZIMPORTACIONES',
                FECHADESDE=desde,
                FECHAHASTA=hasta
            )

            cls_inf_importaciones.dtZImportaciones_Cab = pd.DataFrame(rfc_response.get('ZIMPORTACION_CAB', []))
            cls_inf_importaciones.dtZImportaciones_Det = pd.DataFrame(rfc_response.get('ZIMPORTACION_DET', []))
            cls_inf_importaciones.cod_error = rfc_response.get('CODERROR', 0)
            cls_inf_importaciones.des_error = ""

        except Exception as ex:
            cls_inf_importaciones.cod_error = 1
            cls_inf_importaciones.des_error = str(ex)
        finally:
            if bol_cierra and self.dbc_SAP is not None:
                self.dbc_SAP.close()
                self.dbc_SAP = None

        return cls_inf_importaciones

    def abrir_sap(self):
        # Lee los datos de SAP del config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')
        sap_cfg = config['SAP']
        params = {
            'user': sap_cfg['user'],
            'passwd': sap_cfg['passwd'],
            'ashost': sap_cfg['ashost'],
            'sysnr': sap_cfg['sysnr'],
            'client': sap_cfg['client'],
            'lang': sap_cfg.get('lang', 'ES')
        }
        return Connection(**params)
