import pytesseract
import numpy as np
import cv2 
import pytesseract

def plot(x):
    cv2.imshow('',x)
    cv2.waitKey()

filepath=r"Y:\code\electro-colors\.rois\4.bmp\label-0_roi-0-None_z-21100.0_dist-0.0.png"
img = cv2.imread(filepath)

imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                             # Convertimos a escala de grises 

# Binarizacion, permite identificar lo "muy blanco" en escala de grises.
bin_low = 250                                                               # Seleccionamos umbrales muy selectivos
bin_high = 255                                                              # Ya que el blanco que buscamos es practicamente puro
ret, thresh = cv2.threshold(imgray, bin_low, bin_high, cv2.THRESH_BINARY)   # La binarizacion en si.
img = cv2.bitwise_not(thresh)                                                                            # para facilitar la discriminacion del blanco entre lo demas
plot(img)


mask = np.zeros(img.shape, dtype=img.dtype)
cont = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cont = cont[0] if len(cont) == 2 else cont[1] 

for c in cont:
    area = cv2.contourArea(c)
    if area < 500:
        cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)
print(mask.shape)
#mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY) # making it to 2D (removing the channel value)
removed_border = cv2.bitwise_and(img, img, mask=mask) 
cv2.imshow("result", removed_border)
cv2.waitKey()
cv2.destroyAllWindows()

# kernel = np.ones((5, 5), 'uint8')
# ksize = (7, 7)
# image = cv2.blur(thresh, ksize) 
# # dilate_img = cv2.dilate(thresh, kernel, iterations=1)
# plot(image)
# canny = cv2.Canny(thresh, 200, 255, 1)                                 # Detectamos bordes mediante canny

# Encontramos los contornos EXTERNOS
# Esto ya que lo que nos interesa separar electrodos
# Por el momento no nos interesa las letras ni nada
# Porque no dilatamos antes?
# Porque los bordes externos estan muy bien definidos (es una captura de pantalla)
# La dilatacion no nos da una ventaja
# cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
# for c,cnt in enumerate(cnts):                                       # Iteramos sobre los contornos (que ya deben correspoder solo a electrodos)
#     x,y,w,h = cv2.boundingRect(cnt)                                 # Encontramos el rectangulo limitrofe del electrodo correspondiente
#     ROI = canny[y:y+h, x:x+w]                                 # Recortamos la imagen original a solo los limites actuales
#     plot(ROI)

# Adding custom options
custom_config = r'--oem 3 --psm 6'
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # your path may be different
s = pytesseract.image_to_string(img, config=custom_config)
print(s)
print('ok')

