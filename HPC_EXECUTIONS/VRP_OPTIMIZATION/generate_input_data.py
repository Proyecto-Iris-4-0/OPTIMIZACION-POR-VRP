
#Imports de todas las librerías necesarias

import json
from PERSISTENCIA.db_rutas_normalizada import *
import os

#Conjunto de todos los días en los que hay rutas a realizar
dias_rutas=['INV-LUN-P', 'INV-LUN-I', 'INV-MAR', 'INV-MIE-P', 'INV-MIE-I',
'INV-JUE-P', 'INV-JUE-I', 'INV-VIE-P', 'INV-VIE-I', 'INV-SAB-P', 'INV-SAB-I',
'VER-LUN', 'VER-MAR', 'VER-MIE', 'VER-JUE', 'VER-VIE', 'VER-SAB']

#Coordenadas del depósito Urbaser (lugar donde inician todas las rutas)
coor_depUrb={
    'longitud':-2.404958,
    'latitud':42.475294
}

#Coordenadas del Ecoparque (lugar donde terminan todas las rutas)
coor_Ecoparque={
    'longitud':-2.3533665,
    'latitud':42.4323726
}

'''
Este método crea para cada 'dia_ruta' los datos de entrada necesarios para realizar las
optimizaciones y los guarda en un archivo 'dia_ruta.json' en la carpeta input_data. El 
archivo contiene las siguientes claves:

1.contenedores: una lista con todos los contenedores que intervienen en la ruta

2.ciudades: un listado con todas las ciudades/municipios que intervienen en la ruta. 
Teniendo un orden coherente con la matriz de distancias.

3.matriz: matriz de distancias correspondiente a los "centros" de las ciudades.

4.n_vehiculos: Nº de vehículos disponibles ese día, que coincide con el número de rutas 
que salen.

'''

def generateInputData():
    for dia_ruta in dias_rutas:
        ##Accedo al input_data viejo
        path='viejo/'+dia_ruta+'/input_data.json'
        with open(path) as file:
            data_viejo=json.load(file)
        contenedores_nuevo=data_viejo['contenedores']
        contenedores_nuevo.remove('deposito')
        contenedores_nuevo.insert(0, 'depositoUrbaser')
        contenedores_nuevo.insert(1,'Ecoparque')
        ciudades_nuevo=data_viejo['ciudades']
        ciudades_nuevo.remove('dep')
        ciudades_nuevo.insert(0,'depositoUrbaser')
        ciudades_nuevo.insert(1,'Ecoparque')
        matriz=getDMMunGraphhopper(ciudades_nuevo)
        with open('input_data/'+dia_ruta+'.json','w') as wfile:
            json.dump({
                'contenedores':contenedores_nuevo,
                'ciudades':ciudades_nuevo,
                'matriz':matriz,
                'n_vehiculos':len(getRutas2020ByDay(getEstacion(dia_ruta),getDia(dia_ruta),getPar(dia_ruta)))
            }, wfile)



'''
Este método genera una carpeta 'exec_files/dia_ruta' por cada dia_ruta.
En la cual copia los archivos con las modelizaciones de Gurobi necesarias 
para realizar la optimización y las modifica para tomar los datos de entrada pertinentes.

También copia el archivo 'sbatch.cmd' el cual es el encargado de encolar el 
proceso con slurm.

'''

def generateExecFiles():
    for dia_ruta in dias_rutas:
        path='exec_files/'+dia_ruta
        os.mkdir('exec_files/'+dia_ruta)
        os.system('cp GeneralVRP.py '+path+'/GeneralVRP.py')
        os.system('cp GurobiModelo.py ' + path + '/GurobiModelo.py')
        if tienePar(dia_ruta):
            sbatch_name=getEstacion(dia_ruta)[0]+getDia(dia_ruta)[0]+getPar(dia_ruta)[1]+'.cmd'
        else:
            sbatch_name = getEstacion(dia_ruta)[0] + getDia(dia_ruta)[0] +  '.cmd'
        os.system('cp sbatch.cmd ' +path+'/'+ sbatch_name)

        with open ('GurobiVRP.py') as file:
            data=file.read()
            data=data.replace('$$$$', dia_ruta)
        os.system('rm '+path+ '/GurobiVRP.py')
        with open(path+'/GurobiVRP.py','w') as file:
            file.write(data)
        file.close()

