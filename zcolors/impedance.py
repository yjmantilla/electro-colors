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
import json                         # Para guardar algunos metadatos
#--------------------------------------------------------------------------------------------------
#-------------Parametros constantes-----------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

# Definimos dos listas que siguen el mismo orden para representar el mapeo de un color a un valor
# de impendancia: COLOR[i] --> IMPEDANCIA[i].     

# En un futuro la idea es que estas dos listas se obtengan de forma automatica
# desde la imagen. Sin embargo ya que solo en raras ocasiones cambia, por ahora
# se mantiene como un parametro constante en la ejecucion.

Z_COLORS = [(255,0,255),            # Esta lista contiene n-tuplas de 3 posiciones.  
(128,0,128),                        # Cada una representando un color en formato BGR,
(0,0,255)  ,                        # es decir: (B,G,R)                              
(0,0,192)  ,                        
(0,0,128)  ,                        
(0,128,192),                        
(0,192,192),
(0,255,0)  ,
(0,192,0)  ,
(0,128,0)  ,
(192,192,0),
(255,0,0)  ,
(192,0,0)  ,
(128,0,0)  ,
(63,0,0)   ,
(0,0,0)    ]

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
5*K   ,
np.nan]

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

def binarizar_BGR(img,bin_low=250,bin_high=255):
    """Binarizar imagen BGR de acuerdo a unos umbrales.

    Parameters
    ----------
    img : imagen BGR a binarizar
    bin_low : umbral inferior
    bin_high : umbral superior
    
    Returns
    -------
    (imagen binarizada,imagen en gris)
    """
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                             # Convertimos a escala de grises 
                                                                               # para facilitar la discriminacion del blanco entre lo demas
    # Binarizacion, permite identificar lo "muy blanco" en escala de grises.
    ret, thresh = cv2.threshold(imgray, bin_low, bin_high, cv2.THRESH_BINARY)   # La binarizacion en si.
    return thresh,imgray
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

def save_electrodes_images(electrodes,output_dir,prefix='electrode-'):
    """Guardar imagenes de los electrodos en output_dir siguiendo el esquema siguiente:

    output_dir/prefix-{label}_z-{impedancia}_error-{error}.png
    o
    output_dir/prefix-{label}.png
    segun el caso

    Parameters
    ----------
    electrodes : list[list]
        Lista de listas. Cada lista en un electrodos dado por [arreglo_electrodo,label,impedancia,error de mapeo]
        o [arreglo_electrodo,label]
    output_dir : str
        Path de la carpeta raiz donde se quieren guardar los electrodos.
    prefix : str
        Prefijo de los archivos

    Returns
    -------

    None
    """
    if len(electrodes[0])==4:
        for electrode,label,z,error in electrodes:
            cv2.imwrite(os.path.join(output_dir,f"{prefix}{label}_z-{z}_error-{error}.png"), electrode)  # Guardamos el electrodo en la carpeta de salida
    else:
        assert len(electrodes[0])==2
        for electrode,label in electrodes:
            cv2.imwrite(os.path.join(output_dir,f"{prefix}{label}.png"), electrode)  # Guardamos el electrodo en la carpeta de salida

def get_electrodes(filepath,plot=False,waitkey=False,write=False):
    """Obtener electrodos de una imagen de nombre `filename`, dentro de `input_dir`.

    El error de mapeo es la distancia euclidiana entre el color detectado para el electrodo y el color escogido en la escala Z_COLORS.

    Parameters
    ----------
    filepath : str
        Ruta completa de la imagen.
    plot: bool
        Indica si graficar o no la imagen a medida que es procesada.
    waitkey: bool
        Indica si esperar entrada del usuario para seguir con el algoritmo luego
        de graficar una imagen.
        Ignorado si plot es False.

    Returns
    -------
    list[list]:
        lista con listas de 3 posiciones:
            [array del electrodo,numero del electrodo,impedancia,error de mapeo]
    """
    #TODO: Agregar monitoreo (graficas) e historial a la funcion tal como se hizo con remover_exterior
    img_raw = cv2.imread(filepath)              # Lectura de la imagen entrante

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
    e_count=0
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
            e_count+= 1
            # Para mapear vemos el color mas comun del electrodo
            # Este sera el color que compararemos con la escala colores vs impedancia
            # para asi con este color "moda" mapear el electrodo a una impedancia
            colors,counts = np.unique(electrode.copy().reshape(-1, electrode.shape[-1]), axis=0, return_counts=True)            # Obtenemos los colores presentes en el electrodo asi como el conteo de cada uno
            index=np.argmax(counts)                                                                                             # Encontramos el indice del color mas frecuente
            color = colors[index]                                                                                               # A partir del indice obtenemos el color
            z,dist = z_mapping(color,Z_COLORS,Z_VALUES)                                                                         # Con la funcion z_mapping mapeamos el color a una impedancia
                                                                                                                                # TODO: Obtener escala a partir de la imagen mediante una funcion
            electrodes.append([electrode,e_count,z,dist])                                                                         # Agregamos el electrodo,impedancia,distancia actual a la lista de electrodos
                                                                                                                                # La distancia nos sirve como una metrica de error de mapeo, por eso la guardamos
    return electrodes

def get_label(electrode,reference_electrodes):
    """Retorna el label de un electrodo.

    Funcion aun no implementada pero si planificada.

    Parameters
    ----------
    electrode :
        arreglo de la imagen recortada y binarizada del electrodo
    reference_electrodes:
        lista de electrodos de referencia --> [[array electrodo binarizado,label]]

    Returns
    -------
    label del electrodo con maxima correlacion,maxima correlacion
    """
    corrs = [0]*len(reference_electrodes)
    e_size = electrode.shape
    for i,ref in enumerate(reference_electrodes):
        ref_e,ref_label = ref
        ref_size = ref_e.shape
        ref_size = ref_size[::-1]#reversar x,y, por la convencion invertida de opencv
        e_resized = cv2.resize(electrode, dsize=ref_size, interpolation=cv2.INTER_CUBIC)
        corrs[i] = np.abs(np.corrcoef(ref_e.flatten(),e_resized.flatten())[1,0])
    idx =np.argmax(corrs)
    labels = [e[1] for e in reference_electrodes]
    return labels[idx],corrs[idx]

def label_example_electrodes(unlabeled_electrodes,LABELS,OUTPUT_DIR,SAVE_IMAGES):
    """Asociar labels a una lista de electrodos sin estos que conforman el ejemplo para hacer correlacion.

    Parameters
    ----------
    unlabeled_electrodes : list[list]
    Lista de listas. Cada lista en un electrodos dado por [arreglo_electrodo,label,impedancia,error de mapeo]
    o [arreglo_electrodo,label]

    Es la lista obtenida de get_electrodes sobre el archivo de ejemplo.

    LABELS: list[str]
    Lista con los labels de los electrodos organizados en el mismo orden que unlabeled_electrodes

    OUTPUT_DIR: str
    Carpeta de salida para guardar el ejemplo que se utilizo.

    SAVE_IMAGES: bool
    Para decidir si guardar las imagenes de los electrodos con los labels asociados.

    Returns
    -------
    (labeled_electrodes,labeled_example_path)

    labeled_electrodes: list[lists]
    La lista de electrodos tal como la da get_electrodes pero con los labels asociados y binarizados.

    labeled_example_path: carpeta donde se guardarian los datos del ejemplo utilizado
    """

    labeled_example_path = os.path.join(OUTPUT_DIR,'labeled_example')

    os.makedirs(labeled_example_path,exist_ok=True)                            # Creamos la carpeta de salida en caso de que no exista
    labeled_electrodes = deepcopy(unlabeled_electrodes)
    labeled_electrodes = [[binarizar_BGR(e[0])[0],LABELS[i]] for i,e in enumerate(labeled_electrodes)] # binarizamos de una vez

    if SAVE_IMAGES:
        save_electrodes_images(labeled_electrodes,labeled_example_path,prefix='')
    return labeled_electrodes,labeled_example_path

def process_image(image,labeled_electrodes,OUTPUT_DIR,SAVE_IMAGES):
    """Procesa una imagen con ruta `image` dados un electrodos de referencia para la correlacion
    en `labeled_electrodes`. La salida se guarda en `OUTPUT_DIR`.

    Parameters
    ----------
    image : str
    Ruta completa del archivo de la imagen.

    labeled_electrodes:list[list]
    La salida de la funcion label_example_electrodes

    OUTPUT_DIR: str
    Carpeta de salida

    SAVE_IMAGES: bool
    Para decidir si guardar las imagenes de los electrodos con los labels asociados.

    Returns
    -------
    None
    """
    electrodes = get_electrodes(image)             # Obtenemos lista de electrodos de la imagen
    filename = os.path.split(image)[-1]
    output_folder = os.path.join(OUTPUT_DIR,filename)                      # Carpeta de salida donde guardaremos resultados 
    os.makedirs(output_folder,exist_ok=True)                            # Creamos la carpeta de salida en caso de que no exista
    no_images = [x[1:] for x in electrodes]                             # Lista sin las imagenes de los electrodos (para guardar la tabla)
    bin_electrodes = deepcopy(electrodes)
    bin_electrodes = [[binarizar_BGR(e[0])[0],e[1],e[2],e[3]] for e in bin_electrodes] # binarizamos para hacer correlaciones
    labels = [get_label(e[0],labeled_electrodes) for e in bin_electrodes]
    if SAVE_IMAGES:
        electrodes_with_labels=[[e[0],l[0],e[2],e[3]] for e,l in zip(electrodes,labels)]
        save_electrodes_images(electrodes_with_labels,output_folder,prefix='')
    no_images_and_labels = [x+list(y) for x,y in zip(no_images,labels)]
    df = pd.DataFrame(no_images_and_labels,columns=['electrodo','z','z_error','label','label_corr'])      # Creamos Tabla
    tablepath = os.path.join(output_folder,'electrodes')                # Directorio de la tabla
    df.to_html(tablepath+'.html')                                       # Guardamos tabla html de electrodos
    df.to_csv(tablepath+'.csv')                                         # Guardamos tabla csv de electrodos

def process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES):
    """A partir de una imagen de ejemplo con ruta `EXAMPLE` y sus labels en `LABELS` retorna la lista de electrodos etiquetados del ejemplo.

    Parameters
    ----------
    EXAMPLE : str
    Ruta del archivo de la imagen de ejemplo

    LABELS:list[list]
    Lista con las etiquetas en el mismo orden que el retorno de get_electrodes(EXAMPLE)

    OUTPUT_DIR: str
    Carpeta de salida

    SAVE_IMAGES: bool
    Para decidir si guardar las imagenes de los electrodos con los labels asociados.

    Returns
    -------
    None

    """
    # Etiquetar un ejemplo
    unlabeled_electrodes = get_electrodes(EXAMPLE,write=False)

    labeled_electrodes,labeled_example_path = label_example_electrodes(unlabeled_electrodes,LABELS,OUTPUT_DIR,SAVE_IMAGES)
    with open(os.path.join(labeled_example_path,'example_file.txt'), 'w') as outfile:
        json.dump({'example_file':EXAMPLE}, outfile)
    return labeled_electrodes
