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


import os                           # Para manipulacion de rutas
from glob import glob               # Para listado de archivos
import pandas as pd                 # Para manipulacion de tablas
from copy import deepcopy           # Para copias profundas de variables
import matplotlib.pyplot as plt     # Para graficacion

PATH = '.output'                    # Carpeta de resultados del software
files = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], '*.csv'))] # Busqueda de tablas csv

dfs = []                            # Creamos un solo dataframe con las tablas de todos los archivos
file_metrics = []                   # Variable para guardar metricas de peor correlacion y distancia de cada archivo

# Recoleccion de resultados archivo por archivo
for f in files:                                                                                                         # Para cada archivo
    print(f)                                                                                                            # Para ver por donde va...
    df = pd.read_csv(f,sep=',')                                                                                         # Importar la tabla
    cols = deepcopy(df.columns)                                                                                         # Extraer columnas de la tabla
    df = df.drop(cols[0], axis=1)                                                                                       # Quitar columna de indice
    df = df.drop(cols[1], axis=1)                                                                                       # Quitar columna de numero de electrodo
    file=[f]*df.shape[0]                                                                                                # Crear vector extendido para asociar archivo de origen a cada datum de electrodo
    df['file']=file                                                                                                     # Expandir tabla con el vector extendido anterior
    dfs.append(deepcopy(df))                                                                                            # Crear copia no mutable en la lista acumladora
    worst_corr=df['label_corr'].min()                                                                                   # Peor correlacion del archivo
    worst_dist=df['color_dist'].max()                                                                                   # Peor distancia del archivo
    bad_label=','.join(df.query(f'label_corr == {worst_corr}')['label'].tolist())                                       # Identificar electrodos asociadoas a la peor correlacion
    bad_color =','.join(df.query(f'color_dist == {worst_dist}')['label'].tolist())                                      # Identificar electrodos asociados a la peor distancia
    bads = 'bad_label = ' + bad_label +' ---- bad_color = ' + bad_color                                                 # String con los electrodos sospechosos de cada archivo
    file_metrics.append(pd.DataFrame({'worst_corr':worst_corr,'worst_dist':worst_dist,'suspects':bads},index=[f]))      # Agregar peor correlacion y distancia a la lista


the_df = pd.concat(dfs)                                                             # Creacion del dataframe con todas las tablas
electrodes=the_df['label'].unique()                                                 # Electrodos unicos

# Boxplot de la distribucion de la peor correlacion a lo largo de los electrodos
the_df.boxplot('label_corr',rot=45,by='label',figsize=(2*len(electrodes),3))
plt.xlabel('Etiqueta')
plt.ylabel('Correlacion')
plt.suptitle('')
plt.title('Distribuciones de la correlacion a lo largo de las etiquetas')
plt.show()

# Boxplot de la distribucion de la peor distancia a lo largo de los electrodos
the_df.boxplot('color_dist',rot=45,by='label',figsize=(2*len(electrodes),3))
plt.xlabel('Etiqueta')
plt.ylabel('Distancia euclideana entre colores')
plt.suptitle('')
plt.title('Distribuciones de la distancia entre colores a lo largo de las etiquetas')
plt.show()


# Analisis de la frecuencia de condiciones no aceptables (archivos sospechosos de error)

file_df = pd.concat(file_metrics)                       # Dataframe de peores correlaciones y peores distancias a lo largo de los archivos
min_acceptable_corr = 0.6                               # Minima Correlacion Aceptable
max_acceptable_dist = 10                                # Maxima Distancia Aceptable
normalize = True                                        # Normalizacion de frecuencias (usa porcentajes en vez de la cantidad de veces)


# Grafica de frecuencia de la peor correlacion siendo mas baja que la minima aceptable
worst_corr = file_df['worst_corr'].apply(lambda x: 'corr >= 0.6' if x >= 0.6 else 'corr < 0.6').value_counts(normalize=normalize)       # Particion sobre cumple o no cumple la condicion aceptable
worst_corr = worst_corr.round(decimals = 3)                                                                                             # Redondeo de frecuencias
worst_corr = worst_corr.apply(lambda x: x*100)                                                                                          # Conversion a porcentaje
worst_corr.plot.pie(autopct='%1.2f%%')                                                                                                  # Grafica
plt.ylabel('')
plt.suptitle('')
plt.title('Frecuencia de la peor correlacion de una imagen')
plt.show()


# Grafica de frecuencia de la peor distancia siendo mas alta que la maxima aceptable
worst_dist = file_df['worst_dist'].apply(lambda x: 'dist >= 10' if x >= 10 else 'dist < 10').value_counts(normalize=normalize)          # Particion sobre cumple o no cumple la condicion aceptable
worst_dist = worst_dist.round(decimals = 3)                                                                                             # Redondeo de frecuencias
worst_dist = worst_dist.apply(lambda x: x*100)                                                                                          # Conversion a porcentaje
worst_dist.plot.pie(autopct='%1.2f%%')                                                                                                  # Grafica
plt.ylabel('')
plt.suptitle('')
plt.title('Frecuencia de la peor distancia de una imagen')
plt.show()


# Busqueda de archivos con mayor probabilidad de error (Archivos Sospechosos)
suspect_files = file_df.query(f'worst_corr <= {min_acceptable_corr} or worst_dist >= {max_acceptable_dist}')                            # Busqueda de los archivos donde alguna de las dos condiciones se incumpla
suspect_files.to_html(os.path.join(PATH,'suspect_files.html'))                                                                          # Guardar lista de archivos sospechosos