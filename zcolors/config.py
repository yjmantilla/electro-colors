import os
import shutil
# Get current path
path = os.path.dirname(os.path.realpath(__file__))#os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'static','_uploads')
CONV_FOLDER = os.path.join(path, 'static','_convert')
TEMP_FOLDER = os.path.join(path, 'static','_temp')

# Make directory if uploads is not exists
dirs = [UPLOAD_FOLDER,CONV_FOLDER,TEMP_FOLDER]
for dir in dirs:
    try:
        shutil.rmtree(dir)
    except:
        pass

for x in [UPLOAD_FOLDER,CONV_FOLDER,TEMP_FOLDER]:
    if not os.path.isdir(x):
        os.makedirs(x,exist_ok=True)

class Config(object):
    UPLOAD_FOLDER = os.path.join(path, 'static','_uploads')
    CONV_FOLDER = os.path.join(path, 'static','_convert')
    TEMP_FOLDER = os.path.join(path, 'static','_temp')
    EXAMPLE = os.path.join(path)
    CACHE_TYPE = "null"