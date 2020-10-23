'''
ARCHIVO DE MODELIZACIÓN DEL VRP
'''
# Given a list of edges, finds the shortest subtour
def subtour(edges, all=False):
    visited = [False] * len(edges)
    cycles = []
    lengths = []
    # selected = [[] for i in range(len(edges))]
    selected = dict()
    for x, y in edges:
        selected.update({x: y})
    nodesx = list(selected.keys())
    zero_cycle = []
    while True:
        if False in visited:
            current = visited.index(False)
            current_node = edges[current][0]
            thiscycle = [current_node]
            while True:
                visited[current] = True
                y = selected[current_node]
                if y not in nodesx:
                    print(selected)
                current_node = y if not visited[nodesx.index(y)] else None
                if current_node is None:
                    break
                current = nodesx.index(current_node)
                thiscycle.append(current_node)
            if 0 not in thiscycle:
                cycles.append(thiscycle)
                lengths.append(len(thiscycle))
            else:
                zero_cycle = thiscycle
            if sum(lengths) + len(zero_cycle) == len(edges):
                break
        else:
            break
    if len(lengths) == 0:
        return []
    else:
        if all:
            return cycles
        else:
            return cycles[lengths.index(min(lengths))]


# Auxiliary methods
def sequence(arcs):
    """sequence: make a list of cities to visit, from set of arcs"""
    succ = {}
    for (i, j, k) in arcs:
        succ[i] = j
    curr = 0  # first node being visited
    sol = [curr]
    for i in range(len(arcs) - 1):
        curr = succ[curr]
        sol.append(curr)
    return sol