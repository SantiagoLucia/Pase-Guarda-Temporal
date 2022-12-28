from requests import post
import multiprocessing as mp
import json
from datetime import datetime
from random import choice
import xmltodict

SALIDA = f'proceso_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'

URL_GENERACION_EXPEDIENTE = 'https://mule.hml3.gdeba.gba.gob.ar/EEServices/generar-caratula'
URL_BLOQUEAR_EXPEDIENTE = 'https://mule.hml3.gdeba.gba.gob.ar/EEServices/bloqueo-expediente'
URL_VINCULAR_DOCUMENTOS = 'https://mule.hml3.gdeba.gba.gob.ar/EEServices/documentos-oficiales'
URL_PASE_DESBLOQUEO = 'https://mule.hml3.gdeba.gba.gob.ar/EEServices/generar-pase'

# Definición de Funciones
def listener(q):

    with open(SALIDA, 'w') as f:
        while True:
            m = q.get()
            if m == 'kill':
                break
            f.write(str(m) + '\n')
            f.flush()



def generar_expediente(q):
    
    # response = post('https://iop.gba.gob.ar/servicios/JWT/1/REST/jwt',
    #     auth=('ws_gdeba_prod_dpma_testgdeba', 'Ws*Hml68'))

    # response = post('https://iop.hml.gba.gob.ar/servicios/JWT/1/REST/jwt',
    #     auth=('ws_gdeba_hml_dpma_wstestgdeba', 'dpma*123'))

    # token = response.content.decode('UTF-8')
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        # 'Authorization': f'Bearer {token}'
    }

    payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
        <Body>
            <generarExpedienteElectronicoCaratulacion xmlns="http://ar.gob.gcaba.ee.services.external/">
                <!-- Optional -->
                <request xmlns="">
                    <descripcion>Expediente de prueba. Carece de motivacion administrativa</descripcion>
                    <empresa>false</empresa>
                    <externo>false</externo>
                    <interno>true</interno>
                    <loggeduser>USERT</loggeduser>
                    <motivo>Expediente de prueba. Carece de motivacion administrativa</motivo>
                    <motivoExterno>Expediente de prueba. Carece de motivacion administrativa</motivoExterno>
                    <observaciones>Expediente de prueba. Carece de motivacion administrativa</observaciones>
                    <selectTrataCod>TEST0001</selectTrataCod>
                    <sistema>GDEBA</sistema>
                    <tieneCuitCuil>false</tieneCuitCuil>
                </request>
            </generarExpedienteElectronicoCaratulacion>
        </Body>
    </Envelope>"""

    r = post(URL_GENERACION_EXPEDIENTE, headers=headers, data=payload)
    numero_expediente = r.text[r.text.find("<return>")+8:r.text.find("</return>")]
    
    payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
        <Body>
            <bloquearExpediente xmlns="http://ar.gob.gcaba.ee.services.external/">
                <sistemaBloqueador xmlns="">GDEBA</sistemaBloqueador>
                <codigoEE xmlns="">{numero_expediente}</codigoEE>
            </bloquearExpediente>
        </Body>
    </Envelope>"""

    if r.status_code == 200:

        r = post(URL_BLOQUEAR_EXPEDIENTE, headers=headers, data=payload)
        
        if r.status_code == 200:
            q.put(numero_expediente)


def crear_lista_expedientes(cantidad):
    m = mp.Manager()
    q = m.Queue()
    pool = mp.Pool()
    lista = []

    jobs = [ pool.apply_async(generar_expediente, args=(q,)) for _ in range(cantidad) ]
    
    for _ in jobs:
        _.get()

    pool.close()
    pool.join()
    q.put(None)

    while True:
        e = q.get()
        if e == None:
            break
        lista.append(e)
    
    return lista


def vincular_hacer_definitivo(queue, expediente):
    
    gedo = choice([
        'IF-2020-14754772-GDEBA-TESTGDEBA',
        'IF-2020-14754733-GDEBA-TESTGDEBA',
        'IF-2020-14754699-GDEBA-TESTGDEBA',
        ])

    # response = post('https://iop.gba.gob.ar/servicios/JWT/1/REST/jwt',
    #     auth=('ws_gdeba_prod_dpma_testgdeba', 'Ws*Hml68'))

    # response = post('https://iop.hml.gba.gob.ar/servicios/JWT/1/REST/jwt',
    #     auth=('ws_gdeba_hml_dpma_wstestgdeba', 'dpma*123'))

    # token = response.content.decode('UTF-8')
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        # 'Authorization': f'Bearer {token}'
    }

    payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
        <Body>
            <vincularDocumentosOficiales xmlns="http://ar.gob.gcaba.ee.services.external/">
                <sistemaUsuario xmlns="">GDEBA</sistemaUsuario>
                <usuario xmlns="">USERT</usuario>
                <codigoEE xmlns="">{expediente}</codigoEE>
                <listaDocumentos xmlns="">{gedo}</listaDocumentos>
            </vincularDocumentosOficiales>
        </Body>
    </Envelope>"""

    r = post(URL_VINCULAR_DOCUMENTOS, headers=headers, data=payload)
    
    p_name = mp.current_process().name
    tiempo = datetime.now()
    queue.put(f'{tiempo} - {p_name} - {r} -> {r.text}')    
    
    if r.status_code == 200:
        payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
            <Body>
                <hacerDefinitivosDocsDeEE xmlns="http://ar.gob.gcaba.ee.services.external/">
                    <!-- Optional -->
                    <request xmlns="">
                        <codigoEE>{expediente}</codigoEE>
                        <sistemaUsuario>GDEBA</sistemaUsuario>
                        <usuario>USERT</usuario>
                    </request>
                </hacerDefinitivosDocsDeEE>
            </Body>
        </Envelope>"""

        r = post(URL_VINCULAR_DOCUMENTOS, headers=headers, data=payload)

        p_name = mp.current_process().name
        tiempo = datetime.now()
        queue.put(f'{tiempo} - {p_name} - {r} -> {r.text}')

        if r.status_code == 200:
            payload = f"""<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                <Body>
                    <generarPaseEEConDesbloqueo xmlns="http://ar.gob.gcaba.ee.services.external/">
                        <!-- Optional -->
                        <datosPase xmlns="">
                            <codigoEE>{expediente}</codigoEE>
                            <esMesaDestino>false</esMesaDestino>
                            <esReparticionDestino>false</esReparticionDestino>
                            <esSectorDestino>false</esSectorDestino>
                            <esUsuarioDestino>true</esUsuarioDestino>
                            <estadoSeleccionado>Tramitación</estadoSeleccionado>
                            <motivoPase>Pase de Prueba</motivoPase>
                            <sistemaOrigen>GDEBA</sistemaOrigen>
                            <usuarioDestino>USERT</usuarioDestino>
                            <usuarioOrigen>USERT</usuarioOrigen>
                        </datosPase>
                    </generarPaseEEConDesbloqueo>
                </Body>
            </Envelope>""".encode('utf-8')

            r = post(URL_PASE_DESBLOQUEO, headers=headers, data=payload)

            p_name = mp.current_process().name
            tiempo = datetime.now()
            queue.put(f'{tiempo} - {p_name} - {r} -> {r.text}')


if __name__ == '__main__':
    
    m = mp.Manager()
    q = m.Queue()
    pool = mp.Pool()

    lista_exp = crear_lista_expedientes(1)

    pool.apply_async(listener, args=(q,))
    jobs = [ pool.apply_async(vincular_hacer_definitivo, args=(q, nro_exp,)) for nro_exp in lista_exp ]

    for _ in jobs:
        _.get()

    q.put('kill')
    pool.close()
    pool.join()