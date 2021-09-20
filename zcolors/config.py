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


import os                                                       # Para manejo de paths
import shutil                                                   # Para remocion de archivos

path = os.path.dirname(os.path.realpath(__file__))              # Obtener path del archivo actual

# Definicion de los directorios subida converion y temporal
UPLOAD_FOLDER = os.path.join(path,'_uploads')
CONV_FOLDER = os.path.join(path,'_convert')
TEMP_FOLDER = os.path.join(path,'_temp')

# Remover conversiones previas
dirs = [UPLOAD_FOLDER,CONV_FOLDER,TEMP_FOLDER]
for dir in dirs:
    try:
        shutil.rmtree(dir)
    except:
        pass

# Crear las carpetas en caso de que no existan
for x in [UPLOAD_FOLDER,CONV_FOLDER,TEMP_FOLDER]:
    if not os.path.isdir(x):
        os.makedirs(x,exist_ok=True)

# Configuracion de la webapp mediante una clase Config que hereda de la clase objeto
class Config(object):
    UPLOAD_FOLDER = os.path.join(path,'_uploads')                       # Carpeta subida
    CONV_FOLDER = os.path.join(path,'_convert')                         # Carpeta de conversion (Archivos Resultantes)
    TEMP_FOLDER = os.path.join(path,'_temp')                            # Carpeta temporal
    EXAMPLE = os.path.join(path)                                        # Ruta del ejemplo
    CACHE_TYPE = "null"                                                 # Evita que la pagina no recargue bien los recursos ya que utiliza lo que tiene en cache.
                                                                        # Ver https://stackoverflow.com/questions/55519452/flask-send-file-is-sending-old-file-instead-of-newest/55519673
    SEND_FILE_MAX_AGE_DEFAULT=0                                         # Linea usada tambien para eliminar el cache y evitar que la pagina no aplique cambios recientes.