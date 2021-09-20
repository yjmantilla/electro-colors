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


"""Modulo con algunas funciones auxiliares para el software."""
import os                                                                             # Para manipulacion del sistema de archivos


# Extensiones a considerar para las imagenes
ALLOWED_EXTENSIONS = {'.png','.TIF' ,'.jpg', '.jpeg', '.gif','.bmp'}


def _get_files(root_path,ALLOWED_EXTENSIONS=None):
    """Escanea un directorio de forma recursiva en busca de archivos.
    Retorna una lista con las rutas absolutas a cada uno  de los archivos encontrados.

    Parameters
    ----------
    root_path : str
        La ruta donde se buscaran los archivos.
    
    ALLOWED_EXTENSIONS : list
        lista de las extensiones a considerar para los archivos. Si es None, todo archivo sera aceptado.

    Returns
    -------
    filepaths : list of str
        Lista que contiene las rutas a cada uno de los archivos.
    """
    filepaths = []                                                                     # Variable para acumular archivos
    for root, dirs, files  in os.walk(root_path, topdown=False):                       # For que recorre de forma recursiva los directorios
        for name in files:                                                             # Recorrido de los archivos en una carpeta
            if ALLOWED_EXTENSIONS is not None:                                         # Verificar si hay filtrado de archivos por extension
                if is_valid_file(name):                                                # Si hay filtrado por extension, verificar que el archivo actual sea de alguna de las extensiones permitidas
                    filepaths.append(os.path.join(root, name))                         # En caso de que si, agregarlo a la lista
            else:
                                                                                       # Si no hay restriccion segun la extension, simplemente agregar cada archivo a la lista acumuladora
                filepaths.append(os.path.join(root, name))
    return filepaths

def is_valid_file(x):
    """Verifica que un archivo de nombre `x` cumpla con alguna de las extensiones permitidas."""
    return any([y in x for y in ALLOWED_EXTENSIONS])

def splitall(path):
    """Separa cada parte de una ruta (`path`) de un achivo.
    
    ver https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html"""
    allparts = []                                                                      # Variable acumuladora de partes

                                                                                       # While para separar hasta donde se pueda
    while 1:
        parts = os.path.split(path)                                                    # os.path.split en dos partes luego del ultimo /
        if parts[0] == path:                                                           # Caso final ruta absoluta
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:                                                         # Caso final ruta relativa
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]                                                            # Caso normal, se puede seguir separando
            allparts.insert(0, parts[1])
    return allparts