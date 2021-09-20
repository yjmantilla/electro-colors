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


# Modulo Inicializador del Software

from flask import Flask                             # Libreria para web development

app = Flask(__name__)                               # Obtener app de flask
from zcolors.config import Config                   # Configuracion por defecto del aplicativo

app.config.from_object(Config)                      # Configuracion de la webapp a partir de la configuracion por defecto

from zcolors import routes                          # Importar endpoints (que estan en el archivo routes) como parte esencial del software