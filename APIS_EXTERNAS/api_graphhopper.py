import pycurl
from io import BytesIO
import json




def getDurationGPHLocal(lon1,lat1,lon2,lat2):
    url = 'http://localhost:8989/route?'
    point1='point='+str(lat1)+'%2C'+str(lon1)
    point2 = 'point=' + str(lat2) + '%2C'+ str(lon2)
    url=url+point1+'&'+point2
    str(lon1)
    b_obj = BytesIO()
    crl = pycurl.Curl()
    cadena_curl = url
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