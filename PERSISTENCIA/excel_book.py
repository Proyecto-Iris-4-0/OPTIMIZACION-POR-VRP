import xlsxwriter

import csv
from PERSISTENCIA import db_rutas_connect as db



def generateTSPbook():
    workbook   = xlsxwriter.Workbook('./rutas_opt_tsp.xlsx')

    paginas={}
    for ruta in db.getRutas2020():
        paginas[ruta]=workbook.add_worksheet(name=ruta)
        contenedores_opt = db.getContsOfRouteOPT(ruta, 2020)
        contenedores_org = db.getContsOfRoute(ruta, 2020)
        i=0
        for contenedor in contenedores_opt:
            city=db.getCity(contenedor)
            coord=db.coordFromId(contenedor)
            orden=i
            direccion=db.getDireccionFromContenedor(contenedor)
            fila=[contenedor,orden,city,coord['latitud'],coord['longitud'],direccion]
            print(fila)
            paginas[ruta].write_row(i,0,fila)
            i=i+1
    workbook.close()


workbook = xlsxwriter.Workbook('./rutas_opt_vrp.xlsx')
dias={'INV-LUN-P': 3, 'INV-LUN-I': 3, 'INV-MAR': 3, 'INV-MIE-P': 3, 'INV-MIE-I': 3, 'INV-JUE-P': 3, 'INV-JUE-I': 3, 'INV-VIE-P': 3, 'INV-VIE-I': 3, 'INV-SAB-P': 4, 'INV-SAB-I': 4, 'VER-LUN': 4, 'VER-MAR': 3, 'VER-MIE': 4, 'VER-JUE': 4, 'VER-VIE': 4, 'VER-SAB': 5}
paginas = {}
for dia in dias.keys():
    for i in range(1,dias[dia]+1):
        dia_ruta=dia+'-ruta'+str(i)
        ruta='ruta'+str(i)
        paginas[ruta] = workbook.add_worksheet(name=dia_ruta)
        contenedores_vrp=db.getContsOfRouteVRP(dia,ruta)
        i = 0
        for contenedor in contenedores_vrp:
            city = db.getCity(contenedor)
            coord = db.coordFromId(contenedor)
            orden = i
            direccion = db.getDireccionFromContenedor(contenedor)
            fila = [contenedor, orden, city, coord['latitud'], coord['longitud'], direccion]

            paginas[ruta].write_row(i, 0, fila)
            i = i + 1
workbook.close()