#!/bin/sh

#SBATCH -N 1                     # nodes
#SBATCH -n 1                     # processes
#SBATCH -c 8                    # cores per task; THIS WILL BE THE NUMBER OF THREADS IN GUROBI
#SBATCH --ntasks-per-node=1      # tasks per node (for intra-node execution)
#SBATCH --time=02:00:00          # wall-clock time limit; PLEASE SET UP TIMELIMIT IN GUROBI ACCORDINGLY
#SBATCH -p long24beron216        # queue
#SBATCH --nodelist=beron216      # this is the only licensed node


## Define the environmental variables

export GUROBI_HOME=/NFS_R1/Calculo/gurobi811/linux64
export PATH=$PATH:/NFS_R1/Calculo/gurobi811/linux64/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/NFS_R1/Calculo/gurobi811/linux64/lib/
export GRB_LICENSE_FILE=/NFS_R1/Calculo/gurobi811/linux64/gurobi.lic

## Run calculation


python tsp.py
