import os
import fitz
import pandas

# Variables
input_folder = "output_new"
output_folder = "output_csv_new"
circunscripciones_path = "input/circunscripciones.csv"

circs = pandas.read_csv(circunscripciones_path)

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

files = os.listdir(input_folder)
#files = ['A13114.pdf']

for file in files:
    print(file)
    doc = fitz.open(os.path.join(os.getcwd(), input_folder, file))

    file_wo_ext = os.path.splitext(file)[0]

    padron = []

    for page in doc:
        print("Parsing Page " + str(page.number) + "/" + str(len(doc)))
        
        dic = page.getText("dict")

        # inicializar variables usadas
        region = ''
        provincia = ''
        comuna = ''

        circs_locales = pandas.DataFrame()

        i = 0
        id_header = len(dic['blocks'])

        for block in dic['blocks']:

            # primero se itera en el encabezado hasta determinar que desaparece
            if i < id_header:
                first_column = block['lines'][0]['spans'][0]['text']

                if (first_column != 'PADRÓN AUDITADO PLEBISCITO NACIONAL 2020') & (first_column[1:29] != 'PADRÓN DEFINITIVO ELECCIONES'):
                    if first_column == '  REGIÓN':
                        region = block['lines'][1]['spans'][0]['text'][2:]

                    elif first_column == '  PROVINCIA':
                        provincia = block['lines'][1]['spans'][0]['text'][2:]

                    elif first_column == '  COMUNA':
                        comuna = block['lines'][1]['spans'][0]['text'][2:]
                        circs_locales = circs[circs.comuna == comuna]
                    
                    elif block['lines'][0]['spans'][0]['text'] == 'NOMBRE':
                        # de aquí en adelante aparecen los datos
                        id_header = i

            
            else:
                # dependiendo de cuantas lineas tiene el bloque (parrafo) es como se interpreta el orden de los campos
                if len(block['lines']) >= 5:
                    nombre = block['lines'][0]['spans'][0]['text']
                    ci = block['lines'][1]['spans'][0]['text']

                    # genero y direccion vienen en el mismo span y hay que dividirlo buscando el primer espacio
                    genero_direccion = block['lines'][2]['spans'][0]['text']
                    gd_index = genero_direccion.find(' ')

                    if gd_index == -1:
                        # no se encontró dirección, por lo que se define que el espacio está al final
                        # para obtener correctamente el substring
                        gd_index  = len(genero_direccion)

                    genero = genero_direccion[:gd_index]

                    direccion = genero_direccion[gd_index+1:]
                    circunscripcion = block['lines'][3]['spans'][0]['text']
                    mesa = block['lines'][4]['spans'][0]['text']

                    indigena = ''

                    if len(block['lines']) >= 6:
                        indigena = block['lines'][5]['spans'][0]['text']


                else:
                    nombre = block['lines'][0]['spans'][0]['text']
                    ci = block['lines'][1]['spans'][0]['text']

                    # ej: ' CONVENTO VIEJO 171 CALLE CONVENTO VIEJO CALLE CONVENTO VIEJO 171 CHIMBARONGO'
                    genero_direccion_circunscripcion = block['lines'][2]['spans'][0]['text']

                    genero_index = genero_direccion_circunscripcion.find(' ')
                    genero = genero_direccion_circunscripcion[:genero_index]

                    # como una circunscripcion puede tener mas de un espacio no se puede saber hasta donde llega la direccion
                    # se busca si hay un match con el listado de circunscripciones de la comuna, como fallback se queda con el último espacio
                    direccion_index = genero_direccion_circunscripcion.rfind(' ')

                    for circ in circs_locales.itertuples():
                        index = genero_direccion_circunscripcion.rfind(circ.circunscripcion)

                        if index > 0:
                            direccion_index = index - 1
                            break

                    direccion = genero_direccion_circunscripcion[genero_index+1:direccion_index]
                    circunscripcion = genero_direccion_circunscripcion[direccion_index+1:]

                    mesa = block['lines'][3]['spans'][0]['text']

                #print(nombre, ci, genero, direccion, circunscripcion, mesa, sep=',')

                padron.append({
                    'Nombre': nombre,
                    'CI': ci,
                    'Genero': genero,
                    'Direccion': direccion,
                    'Circunscripcion': circunscripcion,
                    'Mesa': mesa,
                    'Indigena': indigena,
                    'Region': region,
                    'Provincia': provincia,
                    'Comuna': comuna
                })
        
            i = i + 1
            
        #print('End page')

    padron_df = pandas.DataFrame(padron)
    padron_df.to_csv(os.path.join(output_folder, file_wo_ext + '.csv'), index=False)

print('End')