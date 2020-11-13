#Imports de las librerías necesarias


import csv
import pymongo
from APIS_EXTERNAS.api_graphhopper import *

#Conexiones a Mongo

client = pymongo.MongoClient('localhost', 27017)

db_rutas_normalizada=client['rutas_recogida_normalizada']
contenedores_col=db_rutas_normalizada['contenedores']
trayectos_originales_col=db_rutas_normalizada['trayectos_originales']
trayectos_optimizados_col=db_rutas_normalizada['trayectos_optimizados']
matriz_distancias_col=db_rutas_normalizada['matriz_distancias']
distribucion_contenedores=db_rutas_normalizada['distribucion_contenedores']
municipios_col=db_rutas_normalizada['municipios']
matriz_municipios_col=db_rutas_normalizada['matriz_centros_municipios']
tiempos_vrp_2020_col=db_rutas_normalizada['tiempos_vrp_2020']
tiempos_tsp_2020_col=db_rutas_normalizada['tiempos_2020']
trayectos_vrp_2020_col=db_rutas_normalizada['trayectos_vrp_2020']
contenedores_dias_col=db_rutas_normalizada['contenedor_dia']


'''
Dada una lista de  ids de municipios te devuelve 
su matriz de distancias en segundos según Graphhopper
'''

def getDmMunicipios_Segundos_grphhopper(mun_list):
    matriz=[]
    for municipio1 in mun_list:
        fila=[]
        for municipio2 in mun_list:
            print(municipio1, municipio2)
            tiempo=matriz_municipios_col.find_one({'_id':municipio1+'-'+municipio2+'-graphhopper'})['tiempo']
            tiempo=int(round(tiempo/1000,0))
            fila.append(tiempo)
        matriz.append(fila)
    return matriz


'''
Dada una lista de  contenedores te devuelve su matriz de distancias en segundos
según Graphhopper
'''
def getDm_conts_Segundos_db_grphhopper(cont_list):
    matriz=[]
    for contenedor1 in cont_list:
        fila=[]
        for contenedor2 in cont_list:
            consulta=matriz_distancias_col.find_one({'_id':contenedor1+'-'+contenedor2+'-graphhopper'})
            if consulta!=None:
                tiempo=consulta['tiempo']
                tiempo=int(round(tiempo/1000,0))
        matriz.append(fila)
    return matriz

'''
Dada la id de un contenedor te devuelve el nombre del
municipio al que pertenece
'''

def getCity(cont_id):
    if contenedores_col.find_one({'_id':cont_id})==None:
        print('El contenedor ',cont_id,' no esta en la BD registrado.')
    return contenedores_col.find_one({'_id':cont_id})['nombre_municipio']


'''
Dada una lista de contenedores ordenada, devuelve el tiempo que costaría
recorrerla según Google
'''

def calculateTimeGoogle(cont_list):
    tiempo=0
    for j in range(0,len(cont_list)-1):
        if matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]})!=None:
            tiempo=tiempo+matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]})['tiempo']
        else:
            coords1=coordFromId(cont_list[j])
            coords2=coordFromId(cont_list[j+1])
            print(getDurationGPHLocal(coords1['longitud'],coords1['latitud'],coords2['longitud'],coords2['latitud'])
                  ['paths'][0])

    return tiempo


'''
Dada una lista de contenedores ordenada, devuelve el tiempo que costaría
recorrerla según Graphhopper
'''

def calculateTimeGraphhopper(cont_list):
    tiempo=0
    for j in range(0,len(cont_list)-1):

        if matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]+'-graphhopper'})!=None:
            consulta=matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]+'-graphhopper'})['tiempo']
            t_dm=int(round(consulta/1000,0))
            tiempo=tiempo+t_dm
        else:
            coords1 = coordFromId(cont_list[j])
            coords2 = coordFromId(cont_list[j + 1])
            gph=(getDurationGPHLocal(coords1['longitud'], coords1['latitud'], coords2['longitud'], coords2['latitud'])
                  ['paths'][0])
            tiempo=int(round(gph['time']/1000,0))+tiempo
            matriz_distancias_col.insert_one({
                '_id':cont_list[j]+'-'+cont_list[j+1]+'-graphhopper',
                'cont_inicio':cont_list[j],
                'cont_fin':cont_list[j+1],
                'tiempo':gph['time'],
                'distancia':gph['distance']
            })

    return tiempo

def calculateDistanceGraphhopper(cont_list):
    tiempo=0
    for j in range(0,len(cont_list)-1):

        if matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]+'-graphhopper'})!=None:
            consulta=matriz_distancias_col.find_one({'_id':cont_list[j]+'-'+cont_list[j+1]+'-graphhopper'})['distancia']

            tiempo=tiempo+consulta

        else:
            print('aaa')
        return tiempo




'''
Función auxiliar para ordenar un vector de objeto por el criterio de la componente 
orden del objeto
'''
def orderFunction(o):
    return int(o['orden'])


'''
Devuelve un alista con las ids de todas las rutas del 2020
'''
def getRutas2020():
    ids_rutas=set()
    for fila in trayectos_originales_col.find({'year':2020}):
        ids_rutas.add(fila['cod_ruta'])
    return(list(ids_rutas))


'''
Dada la id de un municipio o de un contenedor, devuelve las coordenadas del contenedor 
o las del centro del municipio
'''
def coordFromId(id_cont):
    coords={}
    if len(id_cont)>3:
        coords={}
        contenedor=contenedores_col.find_one({'_id':id_cont})
        coords['longitud']=contenedor['longitud']
        coords['latitud']=contenedor['latitud']
        return coords
    else:
        municipio=municipios_col.find_one({'_id':id_cont})
        coords['longitud'] = municipio['lon_centro']
        coords['latitud'] = municipio['lat_centro']
        return coords

'''
Dada la id de una ruta y el año, te devuelve la lista de contenedores
que en ella intervienen
'''

def getContsOfRoute(route, year):
    conts = []
    for fila in trayectos_originales_col.find({'year': year, 'cod_ruta': route}):
        conts.append(fila)
    conts.sort(key=orderFunction)
    conts_ids = []

    for cont in conts:
        conts_ids.append(cont['cod_cont'])
    if 'deposito' in conts_ids:
        conts_ids.remove('deposito')
    if 'depositoUrbaser' in conts_ids:
        conts_ids.remove('depositoUrbaser')
    if 'Ecoparque' in conts_ids:
        conts_ids.remove('dep')
    conts_ids.insert(0, 'depositoUrbaser')
    conts_ids.append('Ecoparque')

    return (conts_ids)




def getContsOfRouteOPT(route, year):
    conts = []
    for fila in trayectos_optimizados_col.find({'year': year, 'cod_ruta': route}):
        conts.append(fila)
    conts.sort(key=orderFunction)
    conts_ids = []

    for cont in conts:
        conts_ids.append(cont['cod_cont'])
    if 'deposito' in conts_ids:
        conts_ids.remove('deposito')
    if 'depositoUrbaser' in conts_ids:
        conts_ids.remove('depositoUrbaser')
    if 'Ecoparque' in conts_ids:
        conts_ids.remove('dep')
    conts_ids.insert(0, 'depositoUrbaser')
    conts_ids.append('Ecoparque')

    return (conts_ids)

def getContsOfRouteVRP(dia, ruta):
    conts = []
    for fila in db_rutas_normalizada['trayectos_vrp_2020'].find({'dia': dia, 'ruta': ruta}):
        conts.append(fila)
    conts.sort(key=orderFunction)
    conts_ids = []

    for cont in conts:
        conts_ids.append(cont['cod_cont'])
    if 'deposito' in conts_ids:
        conts_ids.remove('deposito')
    if 'depositoUrbaser' in conts_ids:
        conts_ids.remove('depositoUrbaser')
    if 'Ecoparque' in conts_ids:
        conts_ids.remove('dep')
    conts_ids.insert(0, 'depositoUrbaser')
    conts_ids.append('Ecoparque')

    return (conts_ids)


'''
Dada la id de una ruta y el año, te devuelve la lista de municipios
que en ella intervienen
'''

def getMunsOfRoute(route, year):
    contenedores=getContsOfRoute(route,year)
    if 'depositoUrbaser' in contenedores:
        contenedores.remove('depositoUrbaser')
    if 'Ecoparque' in contenedores:
        contenedores.remove('Ecoparque')
    municipios=set()
    for contenedor in contenedores:
        municipios.add(getCity(contenedor))
    return (municipios)


'''
Dada una estación, día y par, este método devuelve una lista con las ids
de las rutas que se dan ese día

'''

def getRutas2020ByDay(estacion='VER', dia='LUN',par='-P'):
    rutas_return=set()
    for ruta in getRutas2020():
        if (estacion in ruta and dia in ruta):
            if ruta[len(ruta)-2:]==par or (ruta[len(ruta)-2:]!='-I'and ruta[len(ruta)-2:]!='-P'):


                rutas_return.add(ruta)
    return rutas_return


'''
Dada la id de un contenedor te devuelve su direccion
'''

def getDireccionFromContenedor(cont_id):
    consulta=contenedores_col.find_one(cont_id)
    if 'direccion' in consulta.keys():
        return consulta['direccion']
    else:
        return ''

'''
Devuelve los contenedores que son recogidos en una
estación, día y "par" concretos
'''

def getContsInDay(estacion='INV',dia='LUN',par='-P'):
    rutas=getRutas2020ByDay(estacion=estacion,dia=dia,par=par)
    contenedores=set()
    for ruta in rutas:
        contenedores=contenedores.union(getContsOfRoute(ruta,2020))
    return contenedores


'''
Método que genera la matriz de distancias correspondiente a 
a la lista de contenedores que se le pasa por parámetro
'''

def getDMGraphhopper(cont_list):
    print('generando la matriz con estos contenedores:',cont_list)
    matrix=[]
    for contenedor1 in cont_list:
        fila=[]
        for contenedor2 in cont_list:
            consulta=matriz_distancias_col.find_one({'_id':contenedor1+'-'+contenedor2+'-graphhopper'})
            if consulta==None:
                print('rellenando DB..')
                elemento={}
                elemento['_id']=contenedor1+'-'+contenedor2+'-graphhopper'
                elemento['cont_inicio']=contenedor1
                elemento['cont_fin'] = contenedor2
                coord1=coordFromId(contenedor1)
                coord2=coordFromId(contenedor2)
                ors=getDurationGPHLocal(coord1['longitud'],coord1['latitud'],
                                    coord2['longitud'],coord2['latitud'])
                if 'paths' not in ors.keys():
                    print(ors)
                    print(contenedor1, contenedor2)


                elemento['tiempo'] =int(round( ors['paths'][0]['time']/1000,0))
                elemento['distancia'] = ors['paths'][0]['distance']
                matriz_distancias_col.insert_one(elemento)
                fila.append(int(round(elemento['tiempo']/1000,0)))
            else:
                fila.append(int(round(consulta['tiempo']/1000,0)))
        matrix.append(fila)
    return matrix

'''

Dado el id de un municipio devuelve su nombre

'''

def getNomFromId(id_mun):
    if len(id_mun)>3:
        return(id_mun)
    else:
        return(municipios_col.find_one({'_id':id_mun})['nombre_municipio'])

'''

Dada una lista de municipios devuelve su matriz de distancias asociada

'''

def getDMMunGraphhopper(mun_list):
    print('generando la matriz con estos contenedores:',mun_list)
    matrix=[]
    for municipio1 in mun_list:
        fila=[]
        for municipio2 in mun_list:
            consulta=matriz_distancias_col.find_one({'_id':municipio1+'-'+municipio2+'-graphhopper'})
            if consulta==None:
                print('rellenando DB..')
                elemento={}
                elemento['_id']=municipio1+'-'+municipio2+'-graphhopper'
                elemento['id_inicio']=municipio1
                elemento['id_fin'] = municipio2
                elemento['nombre_inicio']=getNomFromId(municipio1)
                elemento['nombre_fin']=getNomFromId(municipio2)

                coord1=coordFromId(municipio1)
                coord2=coordFromId(municipio2)
                ors=getDurationGPHLocal(coord1['longitud'],coord1['latitud'],
                                    coord2['longitud'],coord2['latitud'])
                if 'paths' not in ors.keys():
                    print(ors)
                    print(municipio1, municipio2)


                elemento['tiempo'] = int(round(ors['paths'][0]['time'],0))
                elemento['distancia'] = ors['paths'][0]['distance']
                elemento['fuente']='graphhopper'
                elemento['unidad']='segundos'
                matriz_distancias_col.insert_one(elemento)
                fila.append(int(round(elemento['tiempo']/1000,0)))
            else:
                fila.append(int(round(consulta['tiempo']/1000,0)))
        matrix.append(fila)
    return matrix


'''
Dado el id de una ruta devuelve su estación 'INV' o 'VER'.
'''
def getEstacion(dia_ruta):
    return dia_ruta[:3]


'''
Dado el id de una ruta devuelve el día en 
el que se realiza 'LUN', 'MAR'...
'''
def getDia(dia_ruta):
    return dia_ruta[4:7]


'''
Dado el id de una ruta devuelve su paridad, '-P', '-I' o nada.
'''
def getPar(dia_ruta):
    if dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-P' or dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-I':
        par = dia_ruta[len(dia_ruta) - 2:len(dia_ruta)]
    else:
        par = '-P'
    return par


'''
Dado el id de una ruta devuelve un booleano en función de si una ruta está dividida
en días pares/impares o no
'''

def tienePar(dia_ruta):
    if dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-P' or dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-I':
        par = True
    else:
        par = False
    return par


'''
Esta función saca una lista con todos los contenedores que se
recogen el 2020
'''

def getConts2020():
    contenedores_r=set()
    for ruta in getRutas2020():
        for contenedor in getContsOfRoute(ruta,2020):
            contenedores_r.add(contenedor)
    return (list(contenedores_r))


def getContPeriodicity(contenedor, estacion):
    periodicidad_quincenal=0
    for fila in contenedores_dias_col.find({'contenedor':contenedor,'estacion':estacion}):
        if fila['estacion']=='VER' or fila['dia']=='MAR':
            periodicidad_quincenal=periodicidad_quincenal+2
        else:
            periodicidad_quincenal=periodicidad_quincenal+1
    return periodicidad_quincenal


'''

'''
def writePeriodicidades():
    with open('periodicidades_invierno.csv','w') as file:
        writer=csv.writer(file)
        writer.writerow(['contenedor','ciudad','direccion','periodicidad' ])
        for contenedor in getConts2020():
            writer.writerow([contenedor, getCity(contenedor),getDireccionFromContenedor(contenedor),getContPeriodicity(contenedor,'INV')/2 ])

dias=['LUN','MAR','MIE','JUE','VIE','SAB']
pares=['-P','-I']

with open('dias_rutas.csv','w') as file:
    writer = csv.writer(file)
    writer.writerow(['estacion', 'dia','par', 'numero contenedores', 'numero rutas', 'contenedores por ruta'])
    for dia in dias:
        n_conts=len(getContsInDay(estacion='VER',dia=dia,par='-P'))
        n_rutas=len(getRutas2020ByDay(estacion='VER',dia=dia,par='-P'))
        writer.writerow(['VER', dia,'P/I',n_conts , n_rutas, round(n_conts/n_rutas,2)])
    for dia in dias:
        if dia!='MAR':
            for par in pares:
                n_conts=len(getContsInDay(estacion='INV',dia=dia,par=par))
                n_rutas=len(getRutas2020ByDay(estacion='INV',dia=dia,par=par))
                writer.writerow(['INV', dia,par,n_conts , n_rutas, round(n_conts/n_rutas,2)])
        else:
            n_conts = len(getContsInDay(estacion='INV', dia=dia, par='-P'))
            n_rutas = len(getRutas2020ByDay(estacion='INV', dia=dia, par='-P'))
            writer.writerow(['INV', dia, 'P/I', n_conts, n_rutas, round(n_conts / n_rutas, 2)])



dias_rutas=['INV-LUN-P', 'INV-LUN-I', 'INV-MAR', 'INV-MIE-P', 'INV-MIE-I',
'INV-JUE-P', 'INV-JUE-I', 'INV-VIE-P', 'INV-VIE-I', 'INV-SAB-P', 'INV-SAB-I',
'VER-LUN', 'VER-MAR', 'VER-MIE', 'VER-JUE', 'VER-VIE', 'VER-SAB']
dias_rutas=['INV-LUN-P', 'INV-LUN-I', 'INV-MIE-P', 'INV-MIE-I',
'INV-JUE-P', 'INV-JUE-I', 'INV-VIE-P', 'INV-VIE-I', 'INV-SAB-P', 'INV-SAB-I']

var={}
#print(len(getRutas2020ByDay('INV','LUN','-P')))
for dia_ruta in dias_rutas:
    estacion = getEstacion(dia_ruta=dia_ruta)
    dia = getDia(dia_ruta=dia_ruta)
    par=getPar(dia_ruta=dia_ruta)
    var[dia_ruta]=len(getRutas2020ByDay(estacion=estacion,dia=dia,par=par))
#print(var)

lista=[]
def order(o):
    return(o['municipio'])
for municipio in municipios_col.find():
    obj={'municipio':municipio['nombre_municipio'],'coordenadas':[municipio['lon_centro'],municipio['lat_centro']]}
    lista.append(obj)

lista.sort(key=order)
print(lista)
with open ('municipios.csv','w') as f:
    csv_writer=csv.writer(f,delimiter=';')
    csv_writer.writerow(['municipio','longitud','latitud'])
    for mun in lista:
        csv_writer.writerow([mun['municipio'],mun['coordenadas'][0],mun['coordenadas'][1]])

