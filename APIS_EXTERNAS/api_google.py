import googlemaps
from itertools import tee
from pymongo import *

client = MongoClient('localhost', 27017)

db_rutas_normalizada=client['rutas_recogida_normalizada']
municipios=db_rutas_normalizada['municipios']
matriz_municipios=db_rutas_normalizada['matriz_centros_municipios']
API_key = 'TuAPIKey'
gmaps = googlemaps.Client(key=API_key)


def getGoogleDist(punto_1_latitude, punto_1_longitude, punto_2_latitude, punto_2_longitude):
    punto_1_coordenadas=(punto_1_latitude, punto_1_longitude)
    punto_2_coordenadas = (punto_2_latitude, punto_2_longitude)
    print(punto_1_coordenadas,punto_2_coordenadas)
    result = gmaps.distance_matrix(punto_1_coordenadas, punto_2_coordenadas, mode='driving')
    print('aa',result)
    tiempo=result['rows'][0]['elements'][0]['duration']['value']
    distancia = result['rows'][0]['elements'][0]['distance']['value']
    return({
        'tiempo':tiempo,
        'distancia':distancia
    })