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
#--------------------------Agosto de 2021----------------------------------------------------------
#--------------------------------------------------------------------------------------------------
import cv2                          # Para el procesamiento de Imagenes
import numpy as np                  # Para manejo de matricesS
import os                           # Para la manipulacion del sistema de archivos
import shutil                       # Para la manipulacion del sistema de archivos
import pandas as pd                 # Para crear la tabla final de electrodos
from copy import deepcopy           # Para hacer copias reales de variables

#--------------------------------------------------------------------------------------------------
#-------------Variables de entrada-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

PLOT = False                        # Para controlar si queremos visualizar el procesamiento
                                    # durante el run-time

INPUT_DIR = 'images'                # Directorio donde se encuentran las imagenes originales
                                    # que se van a procesar.
OUTPUT_DIR = '.rois'                # Directorio donde se va a guardar el resultado de procesamiento
                                    # de cada una de las imagenes.

#--------------------------------------------------------------------------------------------------
#-------------Parametros constantes-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

# Definimos dos listas que siguen el mismo orden para representar el mapeo de un color a un valor
# de impendancia: COLOR[i] --> IMPEDANCIA[i].     

# En un futuro la idea es que estas dos listas se obtengan de forma automatica
# desde la imagen. Sin embargo ya que solo en raras ocasiones cambia, por ahora
# se mantiene como un parametro constante en la ejecucion.

Z_COLORS = [(255,0,255),            # Esta lista contiene n-tuplas de 3 posiciones.  
(128,0,128),                        # Cada una representando un color en formato RGB,
(0,0,255)  ,                        # es decir: (R,G,B)                              
(0,0,192)  ,                        # TODO: Falta colocar el negro, que no esta en la escala
(0,0,128)  ,                        # pero si se usa
(0,128,192),                        
(0,192,192),
(0,255,0)  ,
(0,192,0)  ,
(0,128,0)  ,
(192,192,0),
(255,0,0)  ,
(192,0,0)  ,
(128,0,0)  ,
(63,0,0)   ]

K = 1000                            # Sufijo K para abreviar kilo-ohms
Z_VALUES = [50*K  ,                 # Lista de impedancias, en el mismo orden que los colores
46.8*K,                             # De tal forma que al indexar ambas en un mismo sub-indice
43.6*K,                             # se obtienen el color y la impedancia correspondiente y 
40.4*K,                             # ligados entre si.
37.1*K,                              
33.9*K,                             
30.7*K,
27.5*K,
24.3*K,
21.1*K,
17.9*K,
14.6*K,
11.4*K,
8.2*K ,
5*K   ]

def get_dist(a,b):
    """Calcular distancia euclidiana entre dos tuplas con numeros.

    Util para por ejemplo calcular la distancia entre dos colores.
    Tanto a como b deben tener la misma cantidad de elementos (dimensiones).
    Y ademas las dimensiones deben estar organizadas en el mismo orden.

    Parameters
    ----------
    a : tupla numerica 1
    b : tupla numerica de referencia (la que resta)

    Returns
    -------
    float :
        La distancia euclidiana de `a` respecto a `b`
    """
    ds = []                             # Lista para guardar distancias de cada dimension
    for i,_ in enumerate(a):            # Recorremos a traves de las dimensiones
        ds.append( (a[i]-b[i])**2)      # Distancia componente a componente

    # Ya obtenidas las distancias componente a componente
    # Retornamos la raiz cuadradas de sus sumas
    return np.sqrt(np.sum(ds))          

def z_mapping(bgr,Z_COLORS,Z_VALUES):
    """Mapear un color BGR a una impedancia.

    Esta funcion mapea un color BGR a una impedancia siguiendo un mapeo
    dado por dos listas organizadas que contienen la informacion de la
    escala de colores vs impedancia: 
        Z_COLORS (colores esperados)
        Z_VALUES (impendancias de los colores esperados)
    
    El mapeo del color entrante bgr se logra buscando el color mas cercano a este en Z_COLORS.

    Parameters
    ----------
    bgr : tuple
        Tupla numerica de 3 dimensiones que contiene un color BGR en ese orden.
        Este color es el que intentaremos mapear a una impedancia.
    Z_COLORS : list[tuple]
        Lista de colores esperados (tuplas BGR) dada la escala de colores vs impendancias
    Z_VALUES : list[float]
        Lista de impedancias (flotantes) dada la escala de colores vs impendancias

    Returns
    -------
    tuple:
        (
            float: impedancia,
            float: distancia al color mas cercano en la escala
        )

    """
    # Calculamos la distancia del color entrante a cada uno de los colores de la escala dada
    dists = [get_dist(bgr,o) for o in Z_COLORS]

    # Notemos que `dists` tiene el mismo orden que `Z_COLORS` y `Z_VALUES` 
    # Encontramos el indice de la minima distancia a algun color de la escala
    idx = np.argmin(dists)

    impedancia = Z_VALUES[idx]  # Asignamos la impedancia del color mas cercano de la escala al color entrante
    distancia = dists[idx]      # Guardamos tambien la distancia entre el color entrante y el color de la escala escogido
                                # La distancia nos sirve como una metrica de error de mapeo
                                # Lo deseado es que sea de 0
    return impedancia,distancia # Retorno


def plot_fun(x,title='untitled',func_sig='',plot=True,waitkey=True):
    """Procedimiento auxiliar para graficar y esperar
    la entrada del usuario si es requerido.
    x : np.ndarray
        La imagen a graficar
    title: str
        Titulo de la imagen
    func_sig: str
        Firma para proveer contexto
    plot: bool
        Indica si graficar o no la imagen.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.
    Returns
    -------
    None
    """
    name = func_sig+title
    if plot:                                                # Si modo de graficacion activo
        cv2.imshow(name, x)                                 # Graficamos la imagen
        if waitkey:                                         # Esperamos la entrada del usuario
            cv2.waitKey()                                   # de ser solicitado

def remover_exterior(img,plot=False,waitkey=False):
    """Elimina la ventana externa para quedar solo con 
    los electrodos,la escala y el fondo blanco.

    Parameters
    ----------
    img: arreglo de numpy de una imagen BGR
        La imagen a procesar. Dimensiones (altura,ancho,3 capas de colores)
    plot: bool
        Indica si graficar o no la imagen a medida que es procesada.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.
    Returns
    -------
    tupla con dos listas:
        lista 1: 
            Imagenes en cada fase del proceso.
        lista 2: 
            Label de cada imagen de la lista 1
            ['Imagen Entrante',
            'Imagen Escala de Grises',
            'Imagen Binarizada',
            'Contornos Exteriores',
            'Contorno Maximo: Area Blanca']
    
    El resultado final del proceso estara en la ultima posicion del arreglo ([-1])
    """

    func_signature = 'RemoverExterior:'     # Firma de la funcion para identificar 
                                            # sus impresiones en consola y titulos

    all_images = []                                                 # Lista para ir guardando las imagenes a medida
                                                                    # de que avanzamos en el procesamiento (historial)
    all_titles = []                                                 # Lista para guardar metadatos del historial

    title = 'Imagen Entrante'                                       # Solo una variable para guardar metadatos del historial
    plot_fun(img,title,func_signature,plot,waitkey)                 # Graficacion si es solicitada
    all_images.append(np.copy(img))                                 # Añadir imagen al historial
    all_titles.append(title)                                        # Añadir metadatos
                                                                    # TODO: Este seccion de codigo (title a append) es repetitivo
                                                                    # Se puede colocar en una sola funcion
    # Objetivo: Extraer contornos de aquello que es blanco,
    # es decir, el fondo del interior de la imagen.

    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                             # Convertimos a escala de grises 
                                                                               # para facilitar la discriminacion del blanco entre lo demas
    title = 'Imagen Escala de Grises'                                          # Solo una variable para guardar metadatos del historial
    plot_fun(imgray,title,func_signature,plot,waitkey)                         # Graficacion si es solicitada
    all_images.append(np.copy(imgray))                                         # Añadir imagen al historial
    all_titles.append(title)                                                   # Añadir metadatos

    # Binarizacion, permite identificar lo "muy blanco" en escala de grises.
    bin_low = 250                                                               # Seleccionamos umbrales muy selectivos
    bin_high = 255                                                              # Ya que el blanco que buscamos es practicamente puro
    ret, thresh = cv2.threshold(imgray, bin_low, bin_high, cv2.THRESH_BINARY)   # La binarizacion en si.

    title = 'Imagen Binarizada'                                                 # Solo una variable para guardar metadatos del historial
    plot_fun(thresh,title,func_signature,plot,waitkey)                          # Graficacion si es solicitada
    all_images.append(np.copy(thresh))                                          # Añadir imagen al historial
    all_titles.append(title)                                                    # Añadir metadatos

    # Extraccion de contornos
    # Esto se hara en el modo RETR_EXTERNAL, retornando asi solo los contornos exteriores (del cual el fondo blanco hace parte)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Busqueda de contornos

    # De los contornos extraidos, el fondo blanco sera el contorno mas grande
    # Usamos esta caracteristica para identificarlo

    assert len(contours) != 0,'No se pudieron encontrar contornos.'           # Aseguramos que se haya podido algun contorno
                                                                              # De lo contrario damos error

    # Coloreamos en azul los contornos encontrados para monitorear el algoritmo
    imgcontours  = cv2.drawContours(np.copy(img), contours, -1, 255, 3)       # Coloreamos Contornos
    title = 'Contornos Exteriores'                                            # Solo una variable para guardar metadatos del historial
    plot_fun(imgcontours,title,func_signature,plot,waitkey)                   # Graficacion si es solicitada
    all_images.append(np.copy(imgcontours))                                   # Añadir imagen al historial
    all_titles.append(title)                                                  # Añadir metadatos

    # El contorno mas grande sera el contorno exterior blanco
    # Nuestro objetivo es identificarlo entre todos los contornos
    max_contour = max(contours, key = cv2.contourArea)                        # Encontramos el area del contorno mas grande
                                                                              # cv2.contourArea es la funcion que calcula el area de un contorno
                                                                              # para luego comparar todas las areas y encontrar la mas grande
    x,y,w,h = cv2.boundingRect(max_contour)                                   # Determinamos el rectangulo limitrofe del contorno

    # Recortamos el contorno mas grande, siendo este el resultado final de la funcion
    cropped_image = img[y:y+h, x:x+w]                                         # Recortamos la imagen dado el rectangulo limitrofe
    title = 'Contorno Maximo: Area Blanca'                                    # Solo una variable para guardar metadatos del historial
    plot_fun(cropped_image,title,func_signature,plot,waitkey)                 # Graficacion si es solicitada
    all_images.append(np.copy(cropped_image))                                 # Añadir imagen al historial
    all_titles.append(title)                                                  # Añadir metadatos

    # Para verificar el correcto funcionamiento del algoritmo
    # vemos que el historial y las imagenes guardadas tengan la misma cantidad de elementos
    assert len(all_images) == len(all_titles),'Error, el tamaño del historial no corresponde con la lista de imagenes'
    return all_images,all_titles                                              # Retornamos imagenes y el historial


def is_electrode(area,low=700,high=3000):
    """Determina si un area corresponde a un electrodo dado unos umbrales.

    Parameters
    ----------
    area : numeric
        Area que se quiere clasificar
    low : minima area aceptable para ser electrodo, exclusivo
    high : maxima area aceptable para ser electrodo, exclusivo

    Returns
    -------
    bool :
        True si es electrodo (cumple con los umbrales)
        False en otro caso.
    """
    if area > low and area < high:          # Area dentro del intervalo dado por los umbrales
        return True                         # Si cumple intervalo, es electrodo
    else:                                   # De lo contrario...
        return False                        # NO.

def get_electrodes(filename,input_dir,output_dir,plot=False,waitkey=False):
    """Procesar una sola imagen con nombre `filename`, dentro de `input_dir` y guardarla los resultados en `output_dir`.

    Parameters
    ----------
    filename : str
        Nombre de la imagen dentro de la carpeta `input_dir`
    input_dir : str
        Path de la carpeta donde se encuentra la imagen de nombre `filename`
    output_dir : str
        Path de la carpeta raiz donde se quieren guardar los resultados con el siguiente formato:
        output_dir/filename/roi-{}-{}_z-{}_dist-{}.png
    plot: bool
        Indica si graficar o no la imagen a medida que es procesada.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.


    Returns
    -------
    list[tuple]:
        lista con tuplas de 4 posiciones:
            (array del electrodo,label del electrodo,impedancia,error de mapeo a impedancia)
    """
    #TODO: Agregar monitoreo (graficas) e historial a la funcion tal como se hizo con remover_exterior
    name,ext=os.path.splitext(filename)                                 # Obtenemos nombre y extension del archivo de la imagen
    output_folder = os.path.join(output_dir,name+ext)                   # Carpeta de salida donde guardaremos resultados 
    os.makedirs(output_folder,exist_ok=True)                            # Creamos la carpeta de salida en caso de que no exista
    img_raw = cv2.imread(os.path.join(input_dir,filename))              # Lectura de la imagen entrante

    # Remocion de las ventanas exteriores
    imagenes_remocion,historial_remocion = remover_exterior(img_raw)    # Removemos el "exterior" de la imagen
    img = imagenes_remocion[-1]                                         # Nos quedamos con la imagen recortada a solo la parte interna
    cropped_img = img.copy()                                            # Hacemos una copia inalterada en memoria

    # Segmentacion

    # Primero detectamos bordes mediante Canny
    # Porque antes de Canny no suavizamos? 
    # Porque la imagen al ser una captura de pantalla viene con muy poco ruido
    # Entonces el suavizado no hace mayor efecto sobre el resultado de canny
    canny = cv2.Canny(img, 200, 255, 1)                                 # Detectamos bordes mediante canny

    # Encontramos los contornos EXTERNOS
    # Esto ya que lo que nos interesa separar electrodos
    # Por el momento no nos interesa las letras ni nada
    # Porque no dilatamos antes?
    # Porque los bordes externos estan muy bien definidos (es una captura de pantalla)
    # La dilatacion no nos da una ventaja
    cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # findContours va a retornar 2 o 3 argumentos
    # Este if nos permite quedarnos con los contornos
    # Independientemente de la version
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]


    # Ahora necesitamos discriminar los contornos que son electrodos de los que no
    # Esto lo haremos debido a que el area de un electrodo es practicamente igual siempre

    # Calculamos areas de los contornos
    contour_areas =[]                   # Lista para las areas
    for c in cnts:                      # Iteramos sobre los contornos
        _,_,w,h =cv2.boundingRect(c)    # Obtenemos el rectangulo limitrofe
        contour_areas.append(w*h)       # Calculamos el area como basexaltura

    # Con base en las areas halladas ahora nos quedamos con aquellas que sean de electrodos
    # Usaremos la funcion is_electrode para discriminar electrodos a partir de areas
    electrodes_cnts = [c  for i,c in enumerate(cnts) if is_electrode(contour_areas[i]) ]                # Lista nueva solo con los contornos de electrodos
    electrodes_areas = [contour_areas[i]  for i,c in enumerate(cnts) if is_electrode(contour_areas[i])] # Lista nueva solo con areas de electrodos
    contour_areas = deepcopy(electrodes_areas)                                                          # Reemplazamos la variable original con la version de solo electrodos
    cnts = deepcopy(electrodes_cnts)                                                                    # Reemplazamos la variable original con la version de solo electrodos

    # Ya con solo los contornos que corresponden a electrodos solo nos falta
    # solo nos falta recortar los electrodos, mapearlos a una impedancia
    # y guardarlos/retornarlos

    electrodes = []                                                     # Simplemente una lista para ir guardando los electrodos recortados
    for c,cnt in enumerate(cnts):                                       # Iteramos sobre los contornos (que ya deben correspoder solo a electrodos)
        x,y,w,h = cv2.boundingRect(cnt)                                 # Encontramos el rectangulo limitrofe del electrodo correspondiente
        ROI = cropped_img[y:y+h, x:x+w]                                 # Recortamos la imagen original a solo los limites actuales

        # Debemos manejar el caso de los electrodos outlier (los que estan pegados en la imagen)
        # F5 y FC5
        # La estrategia ya bien sea un contorno normal o el outlier
        # sera colocar en una lista los electrodos hallados en el contorno
        # Y luego iterar sobre ellos para guardarlos

        # Discriminamos si estamos en el caso outlier
        if contour_areas[c] > 1500:                                     # Podemos discriminar este caso ya que este contorno va a tener un
                                                                        # area mayor al de 1 solo electrodo
            # Lo que haremos es picar el contorno en dos
            # En el eje `y` picamos aproximadamente por la mitad
            # En el eje `x` hay un corrimiento entre ambos electrodos
            # por lo que toca agregar ese corrimiento para obtener un buen corte
            # Por ahora los parametros de estos recortes estan puestos a ojo/mano
            # tratando de seguir una proporcionalidad con las dimensiones w,h del contorno
            # quizas haya una manera mas elegante
            ROI1 = cropped_img[y:y+h//2, x+int(np.floor(w*0.25)):x+w]   # Recortamos electrodo superior
            ROI2 = cropped_img[y+h//2:y+h, x:x+int(np.floor(w*0.75))]   # Recortamos electrodo inferior
            ROIS = [ROI1,ROI2]                                          # Colocamos ambos en una lista

        else:                                                           # Este seria el caso de un solo electrodo
            ROIS = [ROI]                                                # Agregamos un solo electrodo a la lista

        # Ya manejado tanto el caso normal como el outlier
        # Simplemente iteramos para mapear/guardar/retornar los electrodos
        for e,electrode in enumerate(ROIS):

            # Para mapear vemos el color mas comun del electrodo
            # Este sera el color que compararemos con la escala colores vs impedancia
            # para asi con este color "moda" mapear el electrodo a una impedancia
            colors,counts = np.unique(electrode.copy().reshape(-1, electrode.shape[-1]), axis=0, return_counts=True)            # Obtenemos los colores presentes en el electrodo asi como el conteo de cada uno
            index=np.argmax(counts)                                                                                             # Encontramos el indice del color mas frecuente
            color = colors[index]                                                                                               # A partir del indice obtenemos el color
            z,dist = z_mapping(color,Z_COLORS,Z_VALUES)                                                                         # Con la funcion z_mapping mapeamos el color a una impedancia
                                                                                                                                # TODO: Obtener escala a partir de la imagen mediante una funcion
            label = get_label(electrode)                                                                                        # Obtenemos el label, esta funcion aun no esta implementada
            electrodes.append((electrode,label,z,dist))                                                                         # Agregamos el electrodo,impedancia,distancia actual a la lista de electrodos
                                                                                                                                # La distancia nos sirve como una metrica de error de mapeo, por eso la guardamos
            cv2.imwrite(os.path.join(output_folder,"label-{}_roi-{}-{}_z-{}_dist-{}.png".format(c,e,label,z,dist)), electrode)  # Guardamos el electrodo en la carpeta de salida
    return electrodes

def get_label(electrode):
    """Retorna el label de un electrodo.

    Funcion aun no implementada pero si planificada.

    Parameters
    ----------
    electrode : arreglo de la imagen recortada del electrodo

    Returns
    -------
    None (por ahora)
    """
    return None
if __name__ == '__main__':                                  # Funcionamiento del programa sobre una carpeta
    listOfFiles = [f for f in os.listdir(INPUT_DIR)]        # Lista de archivos a procesar
    if os.path.isdir(OUTPUT_DIR):                           # Revisar si el directorio de salida ya existe
        shutil.rmtree(OUTPUT_DIR)                           # Limpiarlo en ese caso


    for image in listOfFiles:
        electrodes = get_electrodes(image,INPUT_DIR,OUTPUT_DIR)             # Obtenemos lista de electrodos de la imagen
        output_folder = os.path.join(OUTPUT_DIR,image)                      # Carpeta de salida donde guardaremos resultados 
        os.makedirs(output_folder,exist_ok=True)                            # Creamos la carpeta de salida en caso de que no exista
        no_images = [x[1:] for x in electrodes]                             # Lista sin las imagenes de los electrodos (para guardar la tabla)
        df = pd.DataFrame(no_images,columns=['label','z','error'])          # Creamos Tabla
        tablepath = os.path.join(output_folder,'electrodes')                # Directorio de la tabla
        df.to_html(tablepath+'.html')                                       # Guardamos tabla html de electrodos
        df.to_csv(tablepath+'.csv')                                         # Guardamos tabla csv de electrodos

    print('END')