# VRP_OPTIMIZATION

Esta carpeta tiene el código y la estructura necesaria para realizar la primera fase de la optimización, donde por cada día en el que hay recogida de 
de residuos, se agrupan todos los contenedores por sus municipios, se toma el número de vehículos que estan disponibles ese día y se raliza una optimización siguiendo un modelado por VRP donde los puntos de recogida pasan a ser los centros de municipios, reduciendo así el coste computacional de la opración.
Los archivos que se encargan de la optimización son :

1. GeneralVRP.py
2. GurobiModelo.py
3. GurobiVRP.py

El archivo: 

1.generate_input_data.py 

se encarga de generar la estructura necesaria de ficheros, y los datos de entrada necesarios para que por cada día haya una instancia de optimización.

El archivo:

1. sbatch.cmd

se encarga de encolar los procesos de optimización en un HPC mediante el programa slurm.

El archivo