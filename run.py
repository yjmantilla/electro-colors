import os
import shutil
from electro_colors import process_image,process_example
#--------------------------------------------------------------------------------------------------
#-------------Variables de entrada-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

INPUT_DIR = 'images'                # Directorio donde se encuentran las imagenes originales
                                    # que se van a procesar.
OUTPUT_DIR = '.output'                # Directorio donde se va a guardar el resultado de procesamiento
                                    # de cada una de las imagenes.

SAVE_IMAGES = True                  # Si salvar o no las imagenes de los electrodos individuales

EXAMPLE = 'images/6.bmp'  # La imagen de ejemplo debe tener TODOS los electrodos (ojo con VEO y HEO, ambos deben tener 2 colores contrastados para asegurar buen funcionamiento)
LABELS = ['O1','O2','OZ','PO8','PO7','PO5','PO6','PO4','PO3','POZ','P8','P7','P6','P5','P3','P4','P2','PZ','P1','TP8','TP7','CP6','CP5','CP4','CP2','CPZ','CP1','CP3','C2','CZ','C1','C3','C5','T7','C6','C4','T8','FC2','FCZ','FC4','FC1','FC3','FC6','F1','F2','F4','F3','F5','FC5','F6','FZ','F8','F7','AF3','AF4','FP2','FP1','FPZ','VEO','HEO']

if __name__ == '__main__':                                  # Funcionamiento del programa sobre una carpeta
    listOfFiles = [f for f in os.listdir(INPUT_DIR)]        # Lista de archivos a procesar
    if os.path.isdir(OUTPUT_DIR):                           # Revisar si el directorio de salida ya existe
        shutil.rmtree(OUTPUT_DIR)                           # Limpiarlo en ese caso

    labeled_electrodes=process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES)
    for image in listOfFiles:
        process_image(image,labeled_electrodes,INPUT_DIR,OUTPUT_DIR,SAVE_IMAGES)
    print('END')