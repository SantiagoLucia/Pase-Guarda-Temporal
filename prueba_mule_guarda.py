from requests import post


if __name__ == '__main__':
    
    headers = {'Content-Type': 'text/xml; charset=utf-8'}    
    
    payload = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                <Body>
                    <generarPaseEEConDesbloqueo xmlns="http://ar.gob.gcaba.ee.services.external/">
                        <!-- Optional -->
                        <datosPase xmlns="">
                            <codigoEE>EX-2018-07155988- -GDEBA-SDRRDLP</codigoEE>
                            <esMesaDestino>false</esMesaDestino>
                            <esReparticionDestino>false</esReparticionDestino>
                            <esSectorDestino>false</esSectorDestino>
                            <esUsuarioDestino>false</esUsuarioDestino>
                            <estadoSeleccionado>Guarda Temporal</estadoSeleccionado>
                            <motivoPase>Pase a Guarda Temporal</motivoPase>
                            <sistemaOrigen>GDEBA</sistemaOrigen>
                            <usuarioDestino></usuarioDestino>
                            <usuarioOrigen></usuarioOrigen>
                        </datosPase>
                    </generarPaseEEConDesbloqueo>
                </Body>
            </Envelope>"""
    
    r = post('https://mule.gdeba.gba.gob.ar/EEServices/generar-pase', headers=headers, data=payload)
    
    print(r.content)