from requests import post

URL_GENERACION_EXPEDIENTE = 'https://mule.gdeba.gba.gob.ar/EEServices/generar-caratula'

def generar_expediente():
    
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
    }

    payload = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
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
        
    print(numero_expediente)


if __name__ == '__main__':
    generar_expediente()