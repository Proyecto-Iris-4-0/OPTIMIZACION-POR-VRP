# OPTIMIZACIÓN POR VRP

En este repositorio se encuentra el código necesario para optimización de rutas siguiendo una estrategia en dos pasos,

1. Agrupar los puntos de recogida por municipios, y seguir un modelado de VRP por municipios que tenga en cuenta el número 
de paradas que hay que hacer en cada municipio y el número de vehículos disponibles para ese día.

2. Utilizando los "clusters" de puntos de recogida que surgen de la ejecución del "VRP" (sin tener en cuenta el orden), ejecutar un TSP 
por cada uno de ellos.
