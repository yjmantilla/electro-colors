import pytesseract                                                                       #OCR de python
import numpy as np                                                                      # Librería matematica
import cv2                                                                              # visión computacional


def plot(x):                                                                                 #mostrar imagen
    cv2.imshow('',x)                                                                         # la muestra
    cv2.waitKey()                                                                           #la sostiene

filepath=r"Y:\code\electro-colors\.rois\4.bmp\label-0_roi-0-None_z-21100.0_dist-0.0.png"    # dirección de la imagen
img = cv2.imread(filepath)                                                                   #lectura de la imagen

imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                                              # Convertimos a escala de grises 

# Binarizacion, permite identificar lo "muy blanco" en escala de grises.
bin_low = 250                                                                                # Seleccionamos umbrales muy selectivos
bin_high = 255                                                                              # Ya que el blanco que buscamos es practicamente puro
ret, thresh = cv2.threshold(imgray, bin_low, bin_high, cv2.THRESH_BINARY)                   # La binarizacion en si.
img = cv2.bitwise_not(thresh)                                                               # para facilitar la discriminacion del blanco entre lo demas
plot(img)                                                                                    #mostrar imagen


mask = np.zeros(img.shape, dtype=img.dtype)                                                 #mascara nula
cont = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)                        #encuentra los contornos
cont = cont[0] if len(cont) == 2 else cont[1]                                               # si hay dos coja el primero y de lo contrario agarre el segundo

for c in cont:                                                                               #recorra los contornos
    area = cv2.contourArea(c)                                                                #calcule el area
    if area < 500:                                                                          #si es menor a 500
        cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)                                #dibújela
print(mask.shape)                                                                           #muestrela
removed_border = cv2.bitwise_and(img, img, mask=mask)                                        #aplica operación con la mascara eliminando el fondo
cv2.imshow("result", removed_border)                                                        #muestre el resultado
cv2.waitKey()                                                                                #sostengalo
cv2.destroyAllWindows()                                                                      #destruya las demas ventanas
custom_config = r'--oem 3 --psm 6'                                                          #configuración tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"     # dirección del ejecutable OCR
s = pytesseract.image_to_string(img, config=custom_config)                                  #ejecucioń del OCR
print(s)                                                                                    #imprima el resultad
print('ok')                                                                                #confirmación que todo fue bien

