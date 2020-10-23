'''
ESTE ARCHIVO ENCOLA CON SLURM TODAS LAS EJECUCIONES DE VRP NECESARIAS
'''

import os

def getEstacion(dia_ruta):
    return dia_ruta[:3]

def getDia(dia_ruta):
    return dia_ruta[4:7]

def getPar(dia_ruta):
    if dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-P' or dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-I':
        par = dia_ruta[len(dia_ruta) - 2:len(dia_ruta)]
    else:
        par = '-P'
    return par

def tienePar(dia_ruta):
    if dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-P' or dia_ruta[len(dia_ruta) - 2:len(dia_ruta)] == '-I':
        return True
    else:
        par = '-P'
    return False

dias={'INV-LUN-P': 3, 'INV-LUN-I': 3, 'INV-MAR': 3, 'INV-MIE-P': 3, 'INV-MIE-I': 3, 'INV-JUE-P': 3, 'INV-JUE-I': 3, 'INV-VIE-P': 3, 'INV-VIE-I': 3, 'INV-SAB-P': 4, 'INV-SAB-I': 4, 'VER-LUN': 4, 'VER-MAR': 3, 'VER-MIE': 4, 'VER-JUE': 4, 'VER-VIE': 4, 'VER-SAB': 5}

path_base='exec_files/'

for dia in dias.keys():
    path=path_base+dia
    if not tienePar(dia):
        file=getEstacion(dia)[0]+getDia(dia)[0]+'.cmd'
    else:
        file = getEstacion(dia)[0] + getDia(dia)[0] +getPar(dia)[1] + '.cmd'
        os.chdir(path)
        os.system('sbatch '+file)
        os.chdir('../..')



