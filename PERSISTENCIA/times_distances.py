import csv
from PERSISTENCIA import db_rutas_connect as db
dias={'INV-LUN-P': 3, 'INV-LUN-I': 3, 'INV-MAR': 3, 'INV-MIE-P': 3, 'INV-MIE-I': 3, 'INV-JUE-P': 3, 'INV-JUE-I': 3, 'INV-VIE-P': 3, 'INV-VIE-I': 3, 'INV-SAB-P': 4, 'INV-SAB-I': 4, 'VER-LUN': 4, 'VER-MAR': 3, 'VER-MIE': 4, 'VER-JUE': 4, 'VER-VIE': 4, 'VER-SAB': 5}
with open('tiempos_distancias_dias_vrp.csv',mode='w') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['ruta','segundos_originales','segundos_optimizados','metros_originales','metros_optimizados'])
    n=1
    for dia in dias.keys():
        tiempo_vrp_total=0
        distancia_vrp_total = 0
        tiempo_org_total = 0
        distancia_org_total = 0
        rutas_dia=db.getRutas2020ByDay(db.getEstacion(dia),db.getDia(dia),db.getPar(dia))
        n=1
        for ruta in rutas_dia:
            ruta_vrp='ruta'+str(n)
            n=n+1
            contenedores_opt= db.getContsOfRouteVRP(dia,ruta_vrp)
            contenedores_org= db.getContsOfRoute(ruta,2020)

            segundos_originales=db.calculateTimeGraphhopper(contenedores_org)
            segundos_optimizados= db.calculateTimeGraphhopper(contenedores_opt)
            metros_originales=db.calculateDistanceGraphhopper(contenedores_org)
            metros_optimizados= db.calculateDistanceGraphhopper(contenedores_opt)
            tiempo_vrp_total=tiempo_vrp_total+segundos_optimizados
            distancia_vrp_total = distancia_vrp_total + metros_optimizados
            tiempo_org_total = tiempo_org_total + segundos_originales
            distancia_org_total = distancia_org_total + metros_originales
            if segundos_originales<segundos_optimizados:
                print(ruta,(metros_originales-metros_optimizados)/metros_originales*100,'%')
        fila=[dia,int(round(tiempo_org_total,0)),int(round(tiempo_vrp_total,0)),int(round(distancia_org_total,0)),int(round(distancia_vrp_total,0))]
        writer.writerow(fila)