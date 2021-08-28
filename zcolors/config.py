import os
import shutil
# Get current path
path = os.path.dirname(os.path.realpath(__file__))#os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path,'_uploads')
CONV_FOLDER = os.path.join(path,'_convert')
TEMP_FOLDER = os.path.join(path,'_temp')

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
    UPLOAD_FOLDER = os.path.join(path,'_uploads')
    CONV_FOLDER = os.path.join(path,'_convert')
    TEMP_FOLDER = os.path.join(path,'_temp')
    EXAMPLE = os.path.join(path)
    CACHE_TYPE = "null"
    #https://stackoverflow.com/questions/55519452/flask-send-file-is-sending-old-file-instead-of-newest/55519673
    SEND_FILE_MAX_AGE_DEFAULT=0