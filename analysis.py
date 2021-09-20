import os
from glob import glob
import pandas as pd
from copy import deepcopy
import matplotlib.pyplot as plt
from pandas.core import groupby

PATH = '.output'
files = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], '*.csv'))]

dfs = []
file_metrics = []
for f in files:
    print(f)
    df = pd.read_csv(f,sep=',')
    cols = deepcopy(df.columns)
    df = df.drop(cols[0], axis=1)
    df = df.drop(cols[1], axis=1)
    file=[f]*df.shape[0]
    df['file']=file
    dfs.append(deepcopy(df))
    worst_corr=df['label_corr'].min()
    worst_dist=df['color_dist'].max()
    bad_label=','.join(df.query(f'label_corr == {worst_corr}')['label'].tolist())
    bad_color =','.join(df.query(f'color_dist == {worst_dist}')['label'].tolist())
    bads = 'bad_label = ' + bad_label +' ---- bad_color = ' + bad_color
    file_metrics.append(pd.DataFrame({'worst_corr':worst_corr,'worst_dist':worst_dist,'suspects':bads},index=[f]))


the_df = pd.concat(dfs)
electrodes=the_df['label'].unique()

the_df.boxplot('label_corr',rot=45,by='label',figsize=(2*len(electrodes),3))
plt.xlabel('Etiqueta')
plt.ylabel('Correlacion')
plt.suptitle('')
plt.title('Distribuciones de la correlacion a lo largo de las etiquetas')
plt.show()

the_df.boxplot('color_dist',rot=45,by='label',figsize=(2*len(electrodes),3))
plt.xlabel('Etiqueta')
plt.ylabel('Distancia euclideana entre colores')
plt.suptitle('')
plt.title('Distribuciones de la distancia entre colores a lo largo de las etiquetas')
plt.show()

file_df = pd.concat(file_metrics)
file_df.boxplot(['worst_corr'])
plt.show()

file_df = pd.concat(file_metrics)
file_df.boxplot(['worst_dist'])
plt.show()

import numpy as np
min_acceptable_corr = 0.6
max_acceptable_dist = 10
normalize = True #False
worst_corr = file_df['worst_corr'].apply(lambda x: 'corr >= 0.6' if x >= 0.6 else 'corr < 0.6').value_counts(normalize=normalize)
worst_corr = worst_corr.round(decimals = 3)
worst_corr = worst_corr.apply(lambda x: x*100)
#worst_corr.index = worst_corr.index.to_series()
worst_corr.value_counts(normalize=normalize)
worst_corr.plot.pie(autopct='%1.2f%%')


plt.ylabel('')
plt.suptitle('')
plt.title('Frecuencia de la peor correlacion de una imagen')
plt.show()




worst_dist = file_df['worst_dist'].apply(lambda x: 'dist >= 10' if x >= 10 else 'dist < 10').value_counts(normalize=normalize)

worst_dist = worst_dist.round(decimals = 3)
worst_dist = worst_dist.apply(lambda x: x*100)
#worst_dist.index = worst_dist.index.to_series().apply(lambda x: np.round(x,3))
worst_dist.plot.pie(autopct='%1.2f%%')

plt.ylabel('')
plt.suptitle('')
plt.title('Frecuencia de la peor distancia de una imagen')
plt.show()


# Busqueda de archivos con mayor probabilidad de error



suspect_files = file_df.query(f'worst_corr <= {min_acceptable_corr} or worst_dist >= {max_acceptable_dist}')

suspect_files.shape

suspect_files.to_html(os.path.join(PATH,'suspect_files.html'))
