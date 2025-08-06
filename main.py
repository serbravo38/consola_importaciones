from datetime import datetime, timedelta
from models.funciones import Funciones
from utils.mailer import enviar_aviso_aws

def main():
    carga_importaciones()

def carga_importaciones():
    modelo = Funciones()
    hoy = datetime.now()
    primer_dia_mes = hoy.replace(day=1)
    desde = primer_dia_mes.strftime('%Y%m%d')
    ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    hasta = ultimo_dia_mes.strftime('%Y%m%d')

    print(f"Cargando importaciones desde: {desde} hasta: {hasta}")
    resultado = modelo.fnc_carga_oc(desde, hasta)

    if resultado.cod_error == 0:
        enviar_aviso_aws("Datos cargados exitosamente.", tipo='SES')
        print("Datos cargados exitosamente.")
    else:
        enviar_aviso_aws(f"Error inesperado al cargar los datos: {resultado.des_error}", tipo='SES')
        print(f"Error inesperado al cargar los datos: {resultado.des_error}")

if __name__ == "__main__":
    main()
