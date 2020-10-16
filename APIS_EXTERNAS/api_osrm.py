import pycurl
from io import BytesIO
import json
from persistencia.db_rutas_normalizada import *



# Set URL value

longitud1='-1.9924236888888887'
latitud1='41.963956555555555'
longitud2='-2.30810237'
latitud2='42.44658568'
cadena_curl="http://127.0.0.1:5000/route/v1/driving/"+longitud1+","+latitud1+";"+longitud2+","+latitud2+"?steps=true"

def getDurationOSRM(lon1,lat1,lon2,lat2):
    url = 'http://localhost:8989/route?'
    cadena_curl = "http://127.0.0.1:5000/route/v1/driving/" + str(lon1) + "," + str(lat1) + ";" + str(lon2) + "," + str(lat2) + "?steps=true"
    point1='point='+str(lat1)+'%2C'+str(lon1)
    point2 = 'point=' + str(lat2) + '%2C'+ str(lon2)
    url=url+point1+'&'+point2
    str(lon1)
    b_obj = BytesIO()
    crl = pycurl.Curl()

    crl.setopt(crl.URL, cadena_curl)
    # Write bytes that are utf-8 encoded
    crl.setopt(crl.WRITEDATA, b_obj)
    # Perform a file transfer
    crl.perform()
    # End curl session
    crl.close()
    # Get the content stored in the BytesIO object (in byte characters)
    get_body = b_obj.getvalue()
    # Decode the bytes stored in get_body to HTML and print the result
    #print('Output of GET request:\n%s' % get_body.decode('utf8'))
    var=json.loads(get_body.decode('utf8'))

    return(var)

