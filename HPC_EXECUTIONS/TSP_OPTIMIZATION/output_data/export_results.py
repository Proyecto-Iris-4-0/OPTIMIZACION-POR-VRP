import csv
import json
from PERSISTENCIA.db_rutas_normalizada import *


def volcado_resultados():
    with open('resultados_opt_TSP.csv','w') as file:
        writer=csv.writer(file)
        writer.writerow(['ruta','n_nodos','tiempo_original','tiempo_optimizado','tiempo_opt','gap'])
        for ruta in getRutas2020():
            with open(ruta+'.json') as file:
                output_data=json.load(file)
            contenedores=getContsOfRoute(ruta,2020)
            contenedores.append('depositoUrbaser')
            tiempo_original=int(round(calculateTimeGraphhopper(contenedores),0))
            tiempo_opt=int(round(output_data['coste_ruta'],0))
            n_nodos=output_data['N_nodos']
            t_opt=output_data['tiempo_optimizacion']
            gap=output_data['GAP']
            writer.writerow([ruta,n_nodos,tiempo_original,tiempo_opt,t_opt,gap])

def test_contenedores():
    for ruta in getRutas2020():
        with open(ruta + '.json') as file:
            output_data = json.load(file)
        contenedores_org = set(getContsOfRoute(ruta, 2020))
        contenedores_opt=set(output_data['recorrido'])
        print(ruta, contenedores_org.difference(contenedores_opt), contenedores_opt.difference(contenedores_org))

def test_tiempo():
    for ruta in getRutas2020():
        with open(ruta + '.json') as file:
            output_data = json.load(file)
        contenedores_org = getContsOfRoute(ruta, 2020)
        contenedores_org.append('depositoUrbaser')
        contenedores_opt=output_data['recorrido']
        tiempo_opt=output_data['coste_ruta']
        print(ruta, tiempo_opt, calculateTimeGraphhopper(contenedores_opt))

def volcado_rutas():
    with open('UR-rutas.csv','w') as file:
        writer=csv.writer(file,delimiter=';')
        writer.writerow(['cod_cont','id_ruta','orden','cd_mun','ds_mun','direccion','h_recog','unges_id','anyo'])
        for ruta in getRutas2020():
            with open(ruta+'.json') as file:
                output_data=json.load(file)
            trayecto=output_data['recorrido']
            for i in range(0, len(trayecto)):
                direccion=getDireccionFromContenedor(trayecto[i])
                ruta_w='UR-'+ruta
                cd_mun=trayecto[i][:3]
                ds_mun=getCity(trayecto[i])
                writer.writerow([trayecto[i],ruta_w,str(i),cd_mun,ds_mun,direccion,'','UG5',2020])

def volcado_resultadosDB():
    for ruta in getRutas2020():
        with open(ruta+'.json') as file:
            output_data=json.load(file)
        contenedores=getContsOfRoute(ruta,2020)
        contenedores.append('depositoUrbaser')
        tiempo_original=int(round(calculateTimeGraphhopper(contenedores),0))
        tiempo_opt=int(round(output_data['coste_ruta'],0))
        n_nodos=output_data['N_nodos']
        t_opt=output_data['tiempo_optimizacion']
        gap=output_data['GAP']
        unidad='segundos'
        id=ruta+'-graphhopper-segundos'
        tiempos_tsp_2020_col.insert_one({
            '_id':id,
            'tiempo_original':tiempo_original,
            'tiempo_optimizado':tiempo_opt,
            'gap':gap,
            'fuente':'graphhopper',
            'unidad':'segundos'
        })

test_contenedores()
test_tiempo()