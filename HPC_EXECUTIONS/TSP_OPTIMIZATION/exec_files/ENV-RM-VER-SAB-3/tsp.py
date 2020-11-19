from gurobipy import *
import json
import time


'''
####MODELIZACION GUROBI####
'''

def dfj(model, x, n):
    model.params.LazyConstraints = 1
    model.__data = {0: x}

    return model
'''
Suponemos que en el nodo 1 se encuentra el depósito y en el N el ecoparque
'''

def atsp_basic_initial_sol(funcion_subtours, num_nodes, distance_matrix):
    model = Model("atsp - " + funcion_subtours.__name__)
    x = {}
    for i in range(1, num_nodes + 1):
        for j in range(1, num_nodes + 1):
            # if i != j:
            x[i, j] = model.addVar(vtype=GRB.BINARY, name="x(%s,%s)" % (i, j))  # Variable Xij
            #if i - j == 1:
                #x[i, j].start = 1
            #else:
                #x[i, j].start = 0
    # x[n, 1].start = 1

    model.update()
    model.addConstr(quicksum(x[i, i] for i in range(1, num_nodes + 1)) == 0, "Diagonal")
    model.addConstr(x[num_nodes,1]==1,'epq-dep')
    for i in range(1, num_nodes + 1):
        model.addConstr(quicksum(x[i, j] for j in range(1, num_nodes + 1) if i != j) == 1,
                        "Out(%s)" % i)  # Only one output
        model.addConstr(quicksum(x[j, i] for j in range(1, num_nodes + 1) if i != j) == 1,
                        "In(%s)" % i)  # Only one input

    model.setObjective(quicksum(distance_matrix[i, j] * x[i, j] for (i, j) in x), GRB.MINIMIZE)
    model = funcion_subtours(model, x, num_nodes)
    model.update()

    return model


def subtour(edges, n):
    visited = [False] * n
    cycles = []
    lengths = []
    selected = [[] for i in range(n)]
    for x, y in edges:
        selected[x - 1].append(y - 1)
    while True:
        current = visited.index(False)
        thiscycle = [current + 1]
        while True:
            visited[current] = True
            neighbors = [x for x in selected[current] if not visited[x]]
            if len(neighbors) == 0:
                break
            current = neighbors[0]
            thiscycle.append(current + 1)
        cycles.append(thiscycle)
        lengths.append(len(thiscycle))
        if sum(lengths) == n:
            break
    return cycles[lengths.index(min(lengths))]


def stopModel(model, where):
    global tiempoLimiteOptimizacion, solucionEncontrada, optimizacionParada
    if where == GRB.callback.MIPSOL:  # Encuentra una solución
        model.terminate()
        print('\n---------------------  Optimización interrumpìda  ---------------------\n')
        solucionEncontrada = False
        optimizacionParada = True

    elif where == GRB.Callback.MESSAGE and not optimizacionParada:
        model.terminate()
        print('\n---------------------  Optimización interrumpìda sin resultados  ---------------------\n')
        solucionEncontrada = False
        optimizacionParada = True


def subtourelim(model, where):
    global solucionEncontrada
    solucionEncontrada = False
    if where == GRB.Callback.MIPSOL:
        global n
        x = model.__data[0]
        nodes = range(1, n + 1)
        selected = []
        # make a list of edges selected in the solution
        for i in nodes:
            sol = model.cbGetSolution([x[i, j] for j in nodes])
            selected += [(i, j + 1) for j in range(n) if sol[j] > 0.5]

        # find the shortest cycle in the selected edge list
        tour = subtour(selected, n)
        if 2 <= len(tour) <= n - 1:
            # add a subtour elimination constraint
            model.cbLazy(quicksum(x[i, j] for j in tour for i in tour) <= len(tour) - 1)
        else:
            solucionEncontrada = True

    elif where == GRB.Callback.MESSAGE:
        if solucionEncontrada:
            stopModel(model, GRB.callback.MIPSOL)






def getInputData(path):
    with open(path) as file:
        input_data = json.load(file)
    file.close()
    return input_data


def getSolution(model,contenedores):
    x = model.__data
    aristas = list()
    for i2 in range(1, n + 1):
        for j in range(1, n + 1):

            if round(x[0][i2, j].X, 0) == 1:
                arista = list()
                arista.append(contenedores[i2 - 1])
                arista.append(contenedores[j - 1])
                # print(mun[i],'-->',mun[j])
                aristas.append(arista)
    recorrido = list()
    recorrido.append(aristas[0][0])
    recorrido.append(aristas[0][1])

    m = len(aristas)
    for i3 in range(1, m - 1):
        for j in range(1, m):
            if aristas[j][0] == recorrido[len(recorrido) - 1]:
                recorrido.append(aristas[j][1])
    return (recorrido)

def writeCSV(path,output_var):
    with open(path, 'w') as file:
        json.dump(output_var, file)

def generateC(matrix):
    c = {}
    for i in range(1, len(matrix) + 1):
        for j in range(1, len(matrix) + 1):
            c[(i, j)] = round(matrix[i - 1][j - 1], 0)
    return c

def main():
    ruta='ENV-RM-VER-SAB-3'
    input_path='../../input_data/'+ruta+'.json'
    output_path='../../output_data/'+ruta+'.json'
    input_data=getInputData(input_path)
    matrix=input_data['matriz']
    contenedores=input_data['contenedores']
    global n
    n=len(contenedores)
    c=generateC(matrix)
    time_inicio=int(time.time())
    model = atsp_basic_initial_sol(dfj, n, c)
    model.Params.OutputFlag = 1  # silent mode
    model.setParam('TIME_LIMIT', 3600)
    model.optimize(subtourelim)
    time_fin=int(time.time())
    time_opt=time_fin-time_inicio
    coste_ruta= model.ObjVal
    recorrido=getSolution(model,contenedores)
    output_data={}
    output_data['ruta']=ruta
    output_data['tiempo_optimizacion']=time_opt
    output_data['coste_ruta']=coste_ruta
    output_data['GAP'] = model.MIPGap
    output_data['N_nodos'] = len(recorrido)
    output_data['recorrido']=recorrido

    writeCSV(output_path,output_data)

if __name__ == "__main__":
    main()
