#--------------------------------------------------------------------------------------------------
#--------------------Extraccion de impedancias en escala de color----------------------------------
#--------------------------------------------------------------------------------------------------
#-------------Alexis Rafael del Carmen Ávila Ortiz--------CC 1083555169----------------------------
#-------------alexis.avila@udea.edu.co--------------------Wpp +57 305 2230574----------------------
#--------------------------------------------------------------------------------------------------
#-------------Yorguin José Mantilla Ramos-----------------CC 1127617499----------------------------
#-------------yorguinj.mantilla@udea.edu.co---------------Wpp +57 311 5154452----------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#----------------------Estudiantes Facultad de Ingenieria  ----------------------------------------
#--------Curso Básico de Procesamiento de Imágenes y Visión Artificial-----------------------------
#--------------------------Septiembre de 2021------------------------------------------------------
#--------------------------------------------------------------------------------------------------


import os                                                           # Para manipulacion de rutas
import shutil                                                       # Para eliminacion de carpetas
from zcolors.impedance import process_image,process_example         # Para el Procesamiento de Imagenes
from zcolors.utils import _get_files                                # Para obtener listado de archivos
from traceback import format_exc                                    # Para formateo de excepciones
import json                                                         # Para guardar archivo json


ROOT_DIR = r"Y:\code\electro-colors\.anon"                          # Directorio donde se encuentran las imagenes a procesar
OUTPUT_DIR = '.output'                                              # Directorio donde se van a guarda los resultados de procesamiento
SAVE_IMAGES = True                                                  # Define si salvar o no las imagenes de los electrodos individuales
EXAMPLE = 'images/6.png'                                            # La imagen de ejemplo. 
                                                                    # Esta debe tener TODOS los electrodos (ojo con VEO y HEO, ambos deben tener 2 colores contrastados para asegurar buen funcionamiento)

# Etiquetas de los electrodos, deben tener el mismo orden en el que los electrodos se segmentan por get_electrodes
LABELS = ['O1','O2','OZ','PO8','PO7','PO5','PO6','PO4','PO3','POZ','P8','P7','P6','P5','P3','P4','P2','PZ','P1','TP8','TP7','CP6','CP5','CP4','CP2','CPZ','CP1','CP3','C2','CZ','C1','C3','C5','T7','C6','C4','T8','FC2','FCZ','FC4','FC1','FC3','FC6','F1','F2','F4','F3','F5','FC5','F6','FZ','F8','F7','AF3','AF4','FP2','FP1','FPZ','VEO','HEO']

if __name__ == '__main__':
    listOfFiles = _get_files(ROOT_DIR)                              # Lista de archivos a procesar
    if os.path.isdir(OUTPUT_DIR):                                   # Revisar si el directorio de salida ya existe
        shutil.rmtree(OUTPUT_DIR)                                   # Limpiarlo en ese caso

    labeled_electrodes=process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES)   # Segmentar y Etiquetar ejemplo siguiendo las etiquetas de entrada
    errors=[]                                                                   # Variable acumuladora de errores

    for i,image in enumerate(listOfFiles):                                      # Procesamiento iterativo imagen a imagen
        try:
            output = os.path.join(OUTPUT_DIR,os.path.split(image.replace(ROOT_DIR,''))[0].strip('/').strip('\\'))   # Definicion de la carpeta de salida para la imagen actual
            process_image(image,labeled_electrodes,output,SAVE_IMAGES)                                              # Procesamiento de la imagen
            print(i)                                                                                                # Contador para saber por cual imagen va...
        except:
            errors.append({'file':image,'error':format_exc()})                                                      # Logging de errores
            print('error',i)                                                                                        # Impresion de errores

    with open(os.path.join(OUTPUT_DIR,'errors.txt'), 'w') as outfile:                                               # Guardar historial de errores
        json.dump(errors, outfile,indent=4)

    print('END')