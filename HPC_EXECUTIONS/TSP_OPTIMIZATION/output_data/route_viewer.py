from PERSISTENCIA.db_rutas_normalizada import *

dias=['VER-SAB','INV-MIE-P','INV-MIE-I','VER-JUE']

for dia in dias:
    print('rutas realizadas: ', dia)
    for ruta in getRutas2020():
        if dia in ruta:
            with open(ruta+'.json','r')as file:
                data=json.load(file)
            recorrido=data['recorrido']
            ciudades=[]
            for contenedor in recorrido:
                if contenedor == 'depositoUrbaser':
                    ciudad = contenedor
                    ciudades.append(ciudad)

                elif contenedor=='Ecoparque':

                    ciudades.append('Ecoparque')
                else:
                    ciudad = getCity(contenedor)
                    if ciudades[len(ciudades) - 1] != ciudad:
                        ciudades.append(ciudad)
            print(ruta, ciudades)