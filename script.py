from requests import post
from requests.exceptions import HTTPError
import csv
from pathlib import Path

FILE_PATH_A_PROCESAR = Path('a_procesar.csv')
FILE_PATH_NO_PROCESADO = Path('no_procesado.csv')
HEADER = {'Content-Type': 'text/xml; charset=utf-8'}

def pasar_expediente(numero_expediente, estado_seleccionado, es_usuario_destino, 
                     usuario_destino, usuario_origen, motivo_pase,sistema_origen):
    # Realiza el pase del expediente al estado seleccionado
    # Numero Expediente: 'EX-2022- -99999999-GDEBA-REPARTICION'
    # Estado Seleccionado: 'Guarda Temporal', 'Tramitación', ...
    # Es Usuario Destino: 'true' o 'false'
    # Usuario Destino: USER o false
    # Usuario Origen: el usuario que posee el expediente
    # Motivo Pase
    # Sistema Origen
    
    payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                <Body>
                    <generarPaseEEConDesbloqueo xmlns="http://ar.gob.gcaba.ee.services.external/">
                        <!-- Optional -->
                        <datosPase xmlns="">
                            <codigoEE>{numero_expediente}</codigoEE>
                            <esMesaDestino>false</esMesaDestino>
                            <esReparticionDestino>false</esReparticionDestino>
                            <esSectorDestino>false</esSectorDestino>
                            <esUsuarioDestino>{es_usuario_destino}</esUsuarioDestino>
                            <estadoSeleccionado>{estado_seleccionado}</estadoSeleccionado>
                            <motivoPase>{motivo_pase}</motivoPase>
                            <sistemaOrigen>{sistema_origen}</sistemaOrigen>
                            <usuarioDestino>{usuario_destino}</usuarioDestino>
                            <usuarioOrigen>{usuario_origen}</usuarioOrigen>
                        </datosPase>
                    </generarPaseEEConDesbloqueo>
                </Body>
            </Envelope>""".encode('utf-8')
    
    r = post('https://mule.gdeba.gba.gob.ar/EEServices/generar-pase', headers=HEADER, data=payload)
    return r

def bloquear_expediente(numero_expediente,sistema_bloqueador):
    # bloquea el expediente
    
    payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
        <Body>
            <bloquearExpediente xmlns="http://ar.gob.gcaba.ee.services.external/">
                <sistemaBloqueador xmlns="">{sistema_bloqueador}</sistemaBloqueador>
                <codigoEE xmlns="">{numero_expediente}</codigoEE>
            </bloquearExpediente>
        </Body>
    </Envelope>"""
    
    r = post('https://mule.gdeba.gba.gob.ar/EEServices/bloqueo-expediente', headers=HEADER, data=payload)
    return r     


if __name__ == '__main__':
    
    with FILE_PATH_A_PROCESAR.open(mode='r', encoding='utf-8') as file_a_procesar, \
        FILE_PATH_NO_PROCESADO.open(mode='w', newline='', encoding='utf-8') as file_no_procesado:
        reader = csv.DictReader(file_a_procesar)
        writer = csv.DictWriter(file_no_procesado, fieldnames=['numero_expediente','estado_seleccionado','usuario','sistema'])
        writer.writeheader()
        
        for row in reader:
            try:
                resultado_bloqueo = bloquear_expediente(
                    numero_expediente=row['numero_expediente'],
                    sistema_bloqueador=row['sistema'])
                resultado_bloqueo.raise_for_status()

                resultado_pase = pasar_expediente(
                    numero_expediente=row['numero_expediente'],
                    estado_seleccionado=row['estado_seleccionado'],
                    es_usuario_destino='true',
                    usuario_destino=row['usuario'],
                    usuario_origen=row['usuario'],
                    motivo_pase='Pase para cambio de estado.',
                    sistema_origen=row['sistema']
                )
                resultado_pase.raise_for_status()

                resultado_bloqueo = bloquear_expediente(
                    numero_expediente=row['numero_expediente'],
                    sistema_bloqueador=row['sistema'])
                resultado_bloqueo.raise_for_status()

                resultado_pase = pasar_expediente(
                    numero_expediente=row['numero_expediente'],
                    estado_seleccionado='Guarda Temporal',
                    es_usuario_destino='false',
                    usuario_destino='false',
                    usuario_origen=row['usuario'],
                    motivo_pase='Pase a Guarda Temporal',
                    sistema_origen=row['sistema']
                )
                resultado_pase.raise_for_status()
                
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err} - {row['numero_expediente']}")
                writer.writerow(row)
    
            except Exception as err:
                print(f"Other error occurred: {err} - {row['numero_expediente']}")
                writer.writerow(row)
                
            else:
                print(f"OK - {row['numero_expediente']}")    