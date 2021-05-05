import requests
import pandas as pd
import os

# Variables
input_folder = "input"
circunscripciones_file = "circunscripciones.csv"

total_circ = pd.DataFrame()

request = requests.get('https://pv.servelelecciones.cl/data/elecciones_constitucion/filters/comunas/all.json')
comunas = request.json()

for comuna in comunas:
    print('Comuna: ' + comuna['d'])

    request_circ = requests.get('https://pv.servelelecciones.cl/data/elecciones_constitucion/filters/circ_electoral/bycomuna/' + str(comuna['c']) + '.json')

    circs = pd.json_normalize(request_circ.json())
    circs['comuna'] = comuna['d']

    total_circ = total_circ.append(circs)

total_circ.rename(columns = {'d':'circunscripcion', 'c':'cod_circunscripcion'}, inplace = True)

# guardar archivo
if not os.path.exists(input_folder):
    os.mkdir(input_folder)

circunscripciones_path = os.path.join(input_folder, circunscripciones_file)
total_circ.to_csv(circunscripciones_path, index=False)