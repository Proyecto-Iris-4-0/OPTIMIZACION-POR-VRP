# -*- coding: utf-8 -*-
"""
GurobiModeloVRP.py:  solve the vehicle routing problem (VRP)

formulations implemented:
    - vrp_Beronia -- formulation for the VRP
"""
from gurobipy import *




def vrp(num_nodes, distance_matrix, num_vehicles, nodes_demand, vehicles_capacity=None):
    model = Model("vrp_Beronia")

    # CONSTANTS

    K = []
    for i in range(0,num_vehicles):
        K.append(i)

    N = []  # Set of all of nodes (first node is depot)
    for i in range(0, num_nodes):
        N.append(i)

    # VARIABLES
    model, x, y = addVRPVariables(model, N, K)

    # CONSTRAINTS
    model = addVRPConstraints(model, N, K, x, y, nodes_demand, vehicles_capacity)

    # Objective function
    model = addObjectiveFunction(model, distance_matrix, x, K, N)
    model = dfj(model, x, K, num_nodes)

    model.update()

    return model,x ,y



def addVRPConstraints(model, N, K, x, y, q, Q):

    for i in N:
        if i != 0 and i !=1:
            model.addConstr(quicksum(y[i, k] for k in K) == 1, name="Vehicle(%s)" % i)
        for k in K:
            model.addConstr(quicksum(x[i, j, k] for j in N) == quicksum(x[j, i, k] for j in N),
                            name='c1(%s,%s)' % (i, k))
            model.addConstr(quicksum(x[i, j, k] for j in N) == y[i, k], name='c2(%s,%s)' % (i, k))
    for k in K:
        model.addConstr(quicksum(q[i]* y[i, k] for i in N) <= Q, name='c3(%s)' % k)
        model.addConstr( x[1,0, k] == 1, name='eco-dep(%s)' % k)

    model.addConstr(quicksum(y[0, k] for k in K) == len(K), name='c4')
    model.addConstr(quicksum(y[1, k] for k in K) == len(K), name='Ecoparque')
    model.addConstr(quicksum(x[i, i, k] for i in N for k in K) == 0, name='Diagonal')

    model.update()

    return model


def addVRPVariables(model, N, K):
    x = {}
    y = {}

    for i in N:
        for k in K:
            for j in N:
                x[i, j, k] = model.addVar(vtype=GRB.BINARY,
                                          name="x(%s,%s,%s)" % (i, j, k))  # Variable Xijk

            y[i, k] = model.addVar(vtype=GRB.BINARY, name="y(%s,%s)" % (i, k))

    model.update()
    return model, x, y


def addObjectiveFunction(model, c, x, K, N):
    model.setObjective(
        quicksum(c[i, j] * quicksum(x[i, j, k] for k in K) for i in N for j in N),
        GRB.MINIMIZE)
    model.update()
    return model


def dfj(model, x, vehicles, n):
    model.params.LazyConstraints = 1
    model.__data = [x, vehicles, n]
    model.update()
    return model
