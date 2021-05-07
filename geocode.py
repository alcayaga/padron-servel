import googlemaps
import pandas as pd
import math
import json
import os

# variables
output_folder = 'output_geocode'

with open('config.json',) as f:
    config = json.load(f)

padron = pd.read_csv('output_csv/A13114.csv')
padron = padron.head(6000)

padron.columns = padron.columns.str.lower()

gmaps = googlemaps.Client(key=config['google_maps_key'])

# separar padron con direccion vacía
padron_dir = padron[~padron['direccion'].isnull()].copy()
padron_nodir = padron[padron['direccion'].isnull()]

# obtener dirección sanitizada sin departamento o piso
padron_dir['direccion_limpia'] = padron_dir['direccion'].str.replace(' (OF|D|DEPTO|DEP|DPTO|DP|PISO)(\.)?(\s|/)?[0-9]+.*', '', regex=True)
padron_dir['direccion_completa'] = padron_dir.direccion_limpia + ', ' + padron_dir.comuna

# obtener geocode
padron_dir['latlong'] = padron_dir.direccion_completa.apply(gmaps.geocode)

# separar a los que Google Maps encontró dirección para después extraer latitud y longitud
padron_dir_notfound = padron_dir[padron_dir['latlong'].map(len) == 0]
padron_dir_found = padron_dir[padron_dir['latlong'].map(len) > 0].copy()

# obtener lat y long del primer resultado entregado
padron_dir_found['lat'] = [g[0]['geometry']['location']['lat'] for g in padron_dir_found.latlong]
padron_dir_found['long'] = [g[0]['geometry']['location']['lng'] for g in padron_dir_found.latlong]

# eliminar columnas innecesarias
padron_dir_found = padron_dir_found.drop(['direccion_limpia', 'latlong', 'direccion_completa'], axis=1)
padron_dir_notfound = padron_dir_notfound.drop(['direccion_limpia', 'latlong', 'direccion_completa'], axis=1)

# unificar 3 datasets de vuelta al padrón
padron = padron_dir_found.append([padron_dir_notfound, padron_nodir])

# guardar archivo
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

path = os.path.join(output_folder, 'padron.csv')
padron.to_csv(path)


