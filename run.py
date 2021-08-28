import os
import shutil
from zcolors.impedance import process_image,process_example
from zcolors.utils import _get_files
from traceback import format_exc
import json
#--------------------------------------------------------------------------------------------------
#-------------Variables de entrada-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

ROOT_DIR = r"Y:\code\electro-colors\.images_source"#'.images_source'                # Directorio donde se encuentran las imagenes originales
                                    # que se van a procesar.
OUTPUT_DIR = '.output'                # Directorio donde se va a guardar el resultado de procesamiento
                                    # de cada una de las imagenes.

SAVE_IMAGES = True                  # Si salvar o no las imagenes de los electrodos individuales

EXAMPLE = 'images/6.bmp'  # La imagen de ejemplo debe tener TODOS los electrodos (ojo con VEO y HEO, ambos deben tener 2 colores contrastados para asegurar buen funcionamiento)
LABELS = ['O1','O2','OZ','PO8','PO7','PO5','PO6','PO4','PO3','POZ','P8','P7','P6','P5','P3','P4','P2','PZ','P1','TP8','TP7','CP6','CP5','CP4','CP2','CPZ','CP1','CP3','C2','CZ','C1','C3','C5','T7','C6','C4','T8','FC2','FCZ','FC4','FC1','FC3','FC6','F1','F2','F4','F3','F5','FC5','F6','FZ','F8','F7','AF3','AF4','FP2','FP1','FPZ','VEO','HEO']

if __name__ == '__main__':                                  # Funcionamiento del programa sobre una carpeta
    listOfFiles = _get_files(ROOT_DIR)        # Lista de archivos a procesar
    if os.path.isdir(OUTPUT_DIR):                           # Revisar si el directorio de salida ya existe
        shutil.rmtree(OUTPUT_DIR)                           # Limpiarlo en ese caso

    labeled_electrodes=process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES)
    errors=[]
    for i,image in enumerate(listOfFiles):
        try:
            output = os.path.join(OUTPUT_DIR,os.path.split(image.replace(ROOT_DIR,''))[0].strip('/').strip('\\'))
            process_image(image,labeled_electrodes,output,SAVE_IMAGES)
            print(i)
        except:
            errors.append({'file':image,'error':format_exc()})
            print('error',i)
    with open(os.path.join(OUTPUT_DIR,'errors.txt'), 'w') as outfile:
        json.dump(errors, outfile,indent=4)

    print('END')