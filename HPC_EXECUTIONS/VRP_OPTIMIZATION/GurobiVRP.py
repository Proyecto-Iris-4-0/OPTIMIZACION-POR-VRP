
'''

MODELIZACIÓN DEL vrp
'''

import time

from GeneralVRP import *
from GurobiModelo import *

from gurobipy import *
import json

tiempo = time.time()
n = 0
solucionEncontrada = False


def getContsByCitiesInRoute(ruta):
    contsByCit={}
    with open('../../input_data/'+ruta+'.json') as file:
        input_data=json.load(file)
    conts=input_data['contenedores']
    for cont in conts:
        if cont!='Ecoparque' and cont!= 'depositoUrbaser':
            municipio=cont[:3]
            if municipio not in contsByCit.keys():
                contsByCit[municipio]=list()
                contsByCit[municipio].append(cont)
            else:
                contsByCit[municipio].append(cont)
    contsByCit['Ecoparque']=[]
    contsByCit['depositoUrbaser'] = []
    return contsByCit


# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    global solucionEncontrada

    if where == GRB.Callback.MIPSOL:
        global n
        x = model.__data[0]
        K = model.__data[1]

        nodes = range(n)
        has_subtours = False
        # make a list of edges selected in the solution

        for k in K:
            selected = []
            for i in nodes:
                sol = model.cbGetSolution([x[i, j, k] for j in nodes])
                selected += [(i, j) for j in range(n) if sol[j] > 0.5]

            # find the shortest cycle in the selected edge list
            # subtours = subtour(selected, True)
            tour = subtour(selected, False)
            # for tour in subtours:
            if 2 <= len(tour):
                # add a subtour elimination constraint
                model.cbLazy(
                    quicksum(x[i, j, k] for j in tour for i in tour) <= len(tour) - 1)

                has_subtours = True

        if not has_subtours:
            solucionEncontrada = True
        model.update()
    elif where == GRB.Callback.MESSAGE:
        if solucionEncontrada:
            stopModel(model, GRB.callback.MIPSOL)


def stopModel(model, where):
    global tiempoLimiteOptimizacion, solucionEncontrada, optimizacionParada, tiempo
    try:
        tiempoLimiteOptimizacion
    except NameError:
        tiempoLimiteOptimizacion = None

    if tiempoLimiteOptimizacion is not None:
        diferenciatiempo = int(time.time() - tiempo)

        if where == GRB.callback.MIPSOL and diferenciatiempo >= tiempoLimiteOptimizacion and not optimizacionParada:  # Encuentra una solución
            model.terminate()
            print('\n---------------------  Optimización interrumpìda  ---------------------\n')
            solucionEncontrada = True
            optimizacionParada = True

        elif where == GRB.Callback.MESSAGE and diferenciatiempo >= tiempoLimiteOptimizacion and not optimizacionParada:
            if tiempoLimiteOptimizacion <= 3600:
                tiempoLimiteOptimizacion += tiempoLimiteOptimizacion
            # model.terminate()
            print(
                '\n---------------------  Tiempo de limitación -> %d segundos  ---------------------\n' % tiempoLimiteOptimizacion)
            solucionEncontrada = False
            optimizacionParada = False




def solve_vrp(nodos, num_nodos, c, num_vehicles, output_path, municipios,vehicule_capacity,city_waste, name, tlo=None):
    global tiempo, n, solucionEncontrada, optimizacionParada, tiempoLimiteOptimizacion
    n = num_nodos
    optimizacionParada = False
    solucionEncontrada = False
    opt_time=36000
    tiempo = time.time()


    x={}
    y={}
    model: Model = vrp(n, c, num_vehicles, city_waste, vehicule_capacity)
    y=model[2]
    model=model[0]



    # model.Params.OutputFlag = 1  # silent mode (doesn't show log)

    model._vars = model.getVars()
    model.setParam('TIME_LIMIT',opt_time)
    #model.write(output_path+'.lp')

    model.optimize(subtourelim)


    cost = model.ObjVal
    gap = model.MIPGap
    tiempoCalculo = time.time() - tiempo

    json_logs={}
    json_logs['title']=output_path
    json_logs['opt_time']=str(tiempoCalculo)
    json_logs['coste_rutas']=str(cost)
    json_logs['soluciones']=[]
    json_logs['GAP']=model.MIPGap



    mun=municipios


    print(n, len(mun))

    x = model.__data[0]
    routes = []
    costesRutas = []
    cargasVehiculos = []

    aristas=list()
    for k in range(0,num_vehicles):
        vehiculo=list()

        for i in range(0, n):

            for j in range(0,n):

                if round(x[i,j,k].X,0)==1:
                    arista=list()
                    arista.append(mun[i])
                    arista.append(mun[j])
                    vehiculo.append(arista)
        aristas.append(vehiculo)
    for l in range(0,num_vehicles):
        recorrido=list()
        recorrido.append(aristas[l][0][0])
        recorrido.append(aristas[l][0][1])

        m=len(aristas[l])
        for i in range(1,m-1):
            for j in range(1,m):

                if aristas[l][j][0]==recorrido[len(recorrido)-1]:
                    recorrido.append(aristas[l][j][1])
        json_logs['soluciones'].append(recorrido)

        with open(output_path, 'w') as file:
            json.dump(json_logs, file)

if __name__ == "__main__":
    # Set process priority
    # setProcessPriority()
    dia_ruta='$$$$'
    global tiempoLimiteOptimizacion
    tiempoLimiteOptimizacion = 36000
    output_path='../../output_data/'+dia_ruta+'.json'
    with open('../../input_data/'+dia_ruta+'.json') as file:
        input_data=json.load(file)

    municipios=input_data['ciudades']
    matrix=input_data['matriz']
    n_vehiculos=input_data['n_vehiculos']
    nodos = []
    for i in range(0, len(matrix)):
        nodos.append(i)
    c = {}
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            c[i, j] = matrix[i][j]


    vehicule_capacity=0
    aux=getContsByCitiesInRoute(dia_ruta)
    for key in aux.keys():
        vehicule_capacity=vehicule_capacity+len(aux[key])
    vehicule_capacity=(vehicule_capacity+0.05*vehicule_capacity)/4
    city_waste=[]
    for municipio in municipios:
        city_waste.append(len(aux[municipio]))
    solve_vrp(nodos, len(nodos), c, n_vehiculos, output_path, municipios,400,city_waste,output_path, tlo=tiempoLimiteOptimizacion)


