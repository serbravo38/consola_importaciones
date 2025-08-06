import boto3
import configparser

def enviar_aviso_aws(mensaje, tipo='SES'):
    config = configparser.ConfigParser()
    config.read('config.ini')
    cfg = config['DEFAULT']
    ses = boto3.client(
        'ses',
        aws_access_key_id=cfg['awsAccessKeyId'],
        aws_secret_access_key=cfg['awsSecretAccessKey'],
        region_name=cfg.get('awsRegion', 'us-west-2')
    )
    ses.send_email(
        Source=f"Reporte <{cfg['awsMailFrom']}>",
        Destination={'ToAddresses': [cfg['awsMailTo']]},
        Message={
            'Subject': {'Data': 'Carga OC Importaciones', 'Charset': 'UTF-8'},
            'Body': {'Text': {'Data': mensaje, 'Charset': 'UTF-8'}}
        }
    )
