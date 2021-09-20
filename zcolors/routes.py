from copy import deepcopy # copias profundas para evitar mutaciones de variables no intencionadas
from zcolors import app   # aplicacion web basada en flask
from zcolors import impedance # libreria central del procesamiento de imagenes del software
from zcolors import __path__ as PATH # ruta del modulo zcolors
from zcolors import utils    # funciones auxiliares
PATH = PATH[0] # nos interesa el primer elemento de esta tupla, el cual si corresponde a la ruta en si
import os # para manipulacion de rutas y sistema de archivos
from flask import send_file, render_template,flash,redirect,request,session,send_from_directory # diferentes utilidades flask
import zipfile # para comprimir archivos
from werkzeug.utils import secure_filename # usado para obtener nombres de archivos seguros
from traceback import format_exc # para recolectar los errores que pudiera tener el aplicativo
import cv2 # en este caso usado para la lectura de imagenes
import base64 # para codificar las imagenes
import shutil # para eliminar archivos y carpetas
import json # util para guardar informacion de los errores ocurridos
from datetime import datetime # para retornar la fecha y hora actual
app.secret_key = "secret key"  # llave para el guardado de cookies de la sesion de la aplicacion web

def handle_error(error):
    #"""Funcion para el manejo de un error en el aplicativo"""
    return render_template("error.html", error=error)

def rgb2hex(r,g,b):
    """Conversion de rgb a hex"""
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def show_message(message):
    #"""Funcion para mostrar un mensaje `message` cualquiera a un usuario."""
    return render_template('show_message.html',message=message)

ALLOWED_EXTENSIONS = utils.ALLOWED_EXTENSIONS # Las extensiones permitidas por el software

SCALE = { # Escala por defecto de impedancia-color
    'impedance':impedance.Z_VALUES,
    'colors':[rgb2hex(*color[::-1]) for color in impedance.Z_COLORS] # Recordemos que estos colores estan en BGR, por lo que toca invertir el orden
}

@app.route('/upload/<what_to_upload>', methods=['GET', 'POST']) # decorador del endpoint
def upload_file(what_to_upload='file'):
    #"""Endpoint para subir un ejemplo etiquetado del usuario"""
    if request.method == 'POST': # Si se indico algun archivo (o por otra razon se activo el metodo post)
        # Chequeamos que la consulta tenga en efecto algun archivo
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url) # se recarga la misma pagina

        file = request.files['file'] # en caso de que si se tenga un archivo
        if file.filename == '': # Si el nombre del archivo esta vacio
            flash('No selected file')
            return redirect(request.url) # se recarga la misma pagina
        
        if file and utils.is_valid_file(file.filename): # Si se tiene un archivo con un nombre valido
            filename = secure_filename(file.filename)   # Aseguramos que el nombre  sea seguro
            filename,ext = os.path.splitext(file.filename) # Separamos nombre y extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'example'+ext)) # Guardamos el ejemplo subido en el servidor
            session['example'] = (os.path.join(PATH, '_uploads'),'example'+ext) # Guardamos la ruta del ejemplo en las cookies
            session['labels'] = None # Limpiamos las etiquetas para reasociarlas en un futuro
            img=cv2.imread(os.path.join(*session['example'])) # Leemos el archivo de ejemplo subido
            r, jpg = cv2.imencode('.jpg', img)  # codificamos la imagen como jpg
            jpg_as_text = base64.b64encode(jpg) # convertimos en base64
            data=b'data:image/jpeg;base64,' + jpg_as_text   # Fabricamos una version textual de la imagen codificada en 64 bits
            data=data.decode("utf-8") # Decodificamos en unicode para soporte amplio de items

            # Mostramos la escala con el ejemplo subido por el usuario para que este la verifique en la siguiente pagina
            return render_template('scale.html',edit_mode=True,mode='raw',title='Verify the scale of the software and of the example image is the same',z_values=SCALE['impedance'],colors=SCALE['colors'],example=data)
    return render_template('upload_file.html',what_to_upload=what_to_upload) # si la consulta es get simplemente cargamos la  version pre-subida del template

@app.route('/')
@app.route('/index')
def index():
    #"""Endpoint para mostrar la pagina de inicio"""
    return render_template('index.html')


@app.route('/_uploads/<path:filename>')
def download_file(filename):
    #"""Funcion auxiliar que permite utilizar el archivo `filename` que se encuentra fuera del directorio estatico (static) del servidor"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/scale')
@app.route('/scale/<filename>')
def scale_page(filename=''):
    #"""Endpoint asociado a la escala, ya sea para mostrarla al usuario o para editarla."""
    return render_template('scale.html',edit_mode=False,title='Default Scale',z_values=SCALE['impedance'],colors=SCALE['colors'],example='')

@app.route('/default_example')
def default_example():
    #Endpoint asociado al uso del ejemplo por defecto
    session['example'] = (os.path.join(PATH,'static'),'default_example.bmp') # se guarda en las cookies la ruta del ejemplo por defecto
    with open(os.path.join(session['example'][0],'default_example.txt'), 'r') as f: # Lectura de los labels pre-asociados a ese ejemplo
        session['labels'] = f.readlines() # Guardado de los labels en las cookies

    # Mostramos la escala con el ejemplo por defecto para que el usuario la verifique en la siguiente pagina
    return render_template('scale.html',edit_mode=True,mode='default',title='This is the default example, verify the scale is correct.',z_values=SCALE['impedance'],colors=SCALE['colors'],example='default_example.bmp')

@app.route('/fill_labels')
def fill_labels():
    #"""Funcion para el etiquetado de los electrodos del ejemplo"""

    # Esta funcion viene desde la funcion de verificacion de la escala, por lo tanto primero
    # debemos guardar las impedancias verificadas por el usuario
    impedances = request.args.getlist('impedances') # Obtenemos las impedancias
    session['impedances']=[float(x) for x in impedances] # Las guardamos en las cookies


    example = session['example'][1] # nombre del archivo de ejemplo
    folder = session['example'][0] # Carpeta del archivo de ejemplo
    example_electrodes = impedance.get_electrodes(os.path.join(folder,example)) # Realiza la segmentacion de los electrodos
    encoded_electrodes=[] # variable acumuladora para guardar electrodos codificados para su paso a html
    labels =[] # etiquetas del ejemplo
    for i,e in enumerate(example_electrodes):

        r, jpg = cv2.imencode('.jpg', e[0])         # Codificacion de los electrodos segmentados para ser mostrados en el html

        jpg_as_text = base64.b64encode(jpg)         # Sin tener que guardarlos como archivos separados

        data=b'data:image/jpeg;base64,' + jpg_as_text         # ver https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/40930153
        data=data.decode("utf-8")        # ver https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal
                                         # ver https://stackoverflow.com/questions/606191/convert-bytes-to-a-string

        encoded_electrodes.append(data)  # guardar el electrodo codificado
        labels.append('E'+str(i))        # label por defecto si posteriormente no se asigna ninguno
    if session['labels'] is None:
        session['labels'] = deepcopy(labels) # Actualizacion de los labels si se esta usando el ejemplo por defecto
    return render_template('fill_labels.html',electrodes=encoded_electrodes,labels=session['labels']) # Renderizacion de la pagina de asignacion de etiquetas


@app.route('/upload_folder', methods=['POST', 'GET'])
def upload_folder():
    #"""Funcion para la subida recursiva de una carpeta"""
    if request.method == 'POST': # Si se indico alguna carpeta (o por otra razon se activo el metodo post)
        if 'files[]' not in request.files: # Si la carpeta estaba vacia...
            flash('No Files')   # Avisar que no hay archivos
            return redirect(request.url)    # recargar la pagina
        files = request.files.getlist('files[]') # Obtener la lista de archivos

        # Recursos acerca de la subida de archivos recursiva desde una carpeta
        # https://stackoverflow.com/questions/5826286/how-do-i-use-google-chrome-11s-upload-folder-feature-in-my-own-code/5849341#5849341
        # https://stackoverflow.com/questions/3590058/does-html5-allow-drag-drop-upload-of-folders-or-a-folder-tree
        # https://stackoverflow.com/a/53058574
        # https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/50#files_and_directories
        # https://developer.mozilla.org/en-US/docs/Web/API/File/webkitRelativePath
        # https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory


        filenames = [] # variable acumuladora para guardar los nombres de los archivos encontrados
        files = [f  for f in files if utils.is_valid_file(f.filename)] # Restringimos los archivos a nombres validos segun las restricciones de extensiones aceptadas


        for file in files: # Recorremos la lista de archivos
            if file :
                # util: listado de atributos de un objeto https://stackoverflow.com/questions/2675028/list-attributes-of-an-object
                fileparts = utils.splitall(file.filename) # separamos la ruta del archivo 

                filename = fileparts.pop() # El nombre es la ultima parte, la cual es extraida (y removida) de filename con el pop
                filename = secure_filename(filename) # Aseguramiento del nombre del archivo 
                rel_nested_dir = os.path.join(*fileparts) # ruta relativa del archivo
                abs_nested_dir = os.path.join(app.config['UPLOAD_FOLDER'],'input',rel_nested_dir) # ruta absoluta del archivo
                os.makedirs(abs_nested_dir,exist_ok=True) # Aseguramos que la ruta de salida exista
                file.save(os.path.join(abs_nested_dir, filename)) # Guardamos el archivo en el servidor
                filenames.append(os.path.join(rel_nested_dir,filename).replace('\\','/')) # Agregamos a filenames la ruta relativa a cada archivo 
        return render_template('exclude_files.html', filenames=filenames) # Una vez subidos todo los archivos se procede a la siguiente pagina donde podemos excluir los indeseados

    else: # Si el metodo es get,aun no se han subido los archivos
        # Como venimos de la asignacion de etiquetas. debemos guardar estas
        labels = request.args.getlist('labels') # extraemos las etiquetas dadas por la  pagina anterior
        session['labels']=labels # las guardamos en las cookies

        if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'],'input')):                           # Revisar si el directorio de salida ya existe
            shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'input'))                           # Limpiarlo en ese caso

        return render_template('upload_files.html') # recargar la pagina, ya que aun no se ha subido nada.

@app.route("/init_process", methods=['POST', 'GET'])
def init_process():
    ###"""Funcion para iniciar el procesamiento de las imagenes."""
    if request.method == 'POST': # Si el metodo es post, iniciamos el proesamiento
        listOfFiles = utils._get_files(os.path.join(app.config['UPLOAD_FOLDER'],'input'))        # Lista de archivos a procesar
        if os.path.isdir(app.config['CONV_FOLDER']):                           # Revisar si el directorio de salida ya existe
            shutil.rmtree(app.config['CONV_FOLDER'])                           # Limpiarlo en ese caso
        os.makedirs(app.config['CONV_FOLDER'],exist_ok=True)               # Crear el directorio de salida en caso de que no exista
        example = session['example'][1] # Recuperamos el nombre del archivo ejemplo
        folder = session['example'][0] # Y la carpeta donde esta ubicado

        OUTPUT_DIR = app.config['CONV_FOLDER'] # definimos la carpeta de salida
        EXAMPLE=os.path.join(folder,example) # creamos la ruta completa del archivo de ejemplo
        LABELS=session['labels'] # recuperamos los labels que estaban en las cookies
        ROOT_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'input') # definimos el directorio con las imagenes a procesar (el directorio de subida)
        SAVE_IMAGES=True
        labeled_electrodes=impedance.process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES) # para el ejemplo se segmentan los electrodos y se asocian a los labels proveidos por el usuario
        errors=[] # variable acumuladora para capturar errores que provocan incapacidad de terminar el procesamiento
        for i,image in enumerate(listOfFiles): # recorrido de los archivos
            try:
                # acondicionamiento de la ruta del archivo
                output = os.path.join(OUTPUT_DIR,os.path.split(image.replace(ROOT_DIR,''))[0].strip('/').strip('\\'))
                # procesamiento de cada imagen usando el ejemplo del usuario
                impedance.process_image(image,labeled_electrodes,output,SAVE_IMAGES,Z_VALUES=session['impedances'])
                print(i,image.replace(ROOT_DIR,''))
            except:
                # captura de errores
                errors.append({'file':image,'error':format_exc()})
                print('error',image.replace(ROOT_DIR,''))
        
        # Guardar historial de errores 
        with open(os.path.join(OUTPUT_DIR,'errors.txt'), 'w') as outfile:
            json.dump(errors, outfile,indent=4)
        return render_template("ready.html") # Continuar con la siguiente pagina para avisar al usuario que el procesamiento esta listo
    else: # Si el metodo es get, recargamos la pagina
        return render_template('init_processing.html') 

@app.route("/exclude", methods=['POST', 'GET'])
def exclude():
    #"""Funcion para la exclusion de archivos subidos mediante check boxes"""
    if request.method == "POST": # Si el metodo es post, se prosigue a verificar los archivos, quitando de la lista aquellos que el usuario indico

        filelist = utils._get_files(os.path.join(app.config['UPLOAD_FOLDER'],'input').replace('\\','/')) # Obtenemos la lista completa de archivos
        filelist = [x.replace('\\','/').replace(os.path.join(app.config['UPLOAD_FOLDER'],'input').replace('\\','/')+'/','') for x in filelist] # acondicionamos las rutas para poder compararlas con las proveidas por el formulario html
        include = request.form.getlist('records') # obtenemos la lista dada por el formulario
        filenames = [x for x in filelist if x in include] #  seleccionamos solo aquellos archivos indicados por el usuario
        session['filelist']=filenames # guardamos en las cookies la lista final deseada de archivos a procesar
        return render_template('files.html', filenames=filenames) # renderizamos la pagina siguiente donde se verifica la lista de archivos
    else:
        return render_template('exclude_files.html') # si es get renderizamos la lista de archivos con los check boxes para que el usuario elija cuales procesar


def download_files(list_files,filename):
    #"""Funcion para la descarga de los archivos resultantes"""
    zf = zipfile.ZipFile(filename, "w") # se abre un nuevo archivo zip

    for fpath in list_files: # para cada archivo en la lista de archivos entrante a la funcion
        zip_path = fpath.split("_convert\\")[-1] # obtenemos la ruta relativa respecto a la carpeta _convert
        zf.write(fpath, zip_path) # agregamos el archivo al zip
    zf.close() # cerramos el archivo zip

    # Generamos un texto que indique la fecha y hora de generacion del zip
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S.%f")
    name = f'converted_images_{timestampStr}.zip' # creamos el nombre del zip

    # Recursos para iniciar descarga desde flask
    # See https://stackoverflow.com/a/53390515/14068216
    # https://stackoverflow.com/questions/55519452/flask-send-file-is-sending-old-file-instead-of-newest/55519673
    
    # configuramos la respuesta (la descarga)
    response = send_file(filename, mimetype="application/x-zip-compressed", attachment_filename=name, as_attachment=True,cache_timeout=0)
    response.headers["x-filename"] = name
    response.headers["Access-Control-Expose-Headers"] = 'x-filename'

    return response # retornamos la respuesta, el archivo se descarga

@app.route("/download", methods=["GET"])
def download():
    """Funcion que genera la lista de archivos de la carpeta de conversion, la comprime, e inicia la descarga."""
    files = utils._get_files(app.config['CONV_FOLDER'],None) # generacion de la lista de archivos resultantes
    return download_files(files,os.path.join(app.config['TEMP_FOLDER'],'the_zip.zip')) # compresion y descarga del zip