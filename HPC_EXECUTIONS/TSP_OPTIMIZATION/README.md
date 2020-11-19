# TSP_OPTIMIZATION

Esta carpeta tiene el código y la estructura necesaria para realizar la segunda fase de la optimización, donde previamente hemos ejecutado un VRP a modo de clusterizado 
y ahora con cada cluster ejecutamos un TSP.
El archivo en el que se encuentra la modelización del TSP:

1. TSP_formulation.py


En el archivo: 

1.GENERATE_STRUCTURE.py 

Están todos los métodos necesarios para generar la estructura necesaria de ficheros, y los datos de entrada necesarios para que por cada día haya una instancia de optimización.

Se genera un archivo:

1. sbatch.cmd

por cada ejecución, y cada uno se encarga de encolar el proceso en un HPC mediante el programa slurm.

El archivo:

execute_all.py

Ejecuta todos los archivos sbatch.cmd 

