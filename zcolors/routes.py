from copy import deepcopy
from zcolors import app, config
from zcolors import impedance
from zcolors import __path__ as PATH
from zcolors import utils
PATH = PATH[0]
import os
from flask import render_template,flash,redirect,request,url_for,session,send_from_directory
from werkzeug.utils import secure_filename
from traceback import format_exc
import cv2
import base64
import shutil
import json
from datetime import datetime
app.secret_key = "secret key"

def handle_error(error):
    return render_template("error.html", error=error)

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))

def load_files():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files.get('file')

def show_message(message):
    return render_template('show_message.html',message=message)

ALLOWED_EXTENSIONS = utils.ALLOWED_EXTENSIONS

SCALE = {
    'impedance':impedance.Z_VALUES,
    'colors':[rgb2hex(*color[::-1]) for color in impedance.Z_COLORS]
}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<what_to_upload>', methods=['GET', 'POST'])
def upload_file(what_to_upload='file'):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and utils.is_valid_file(file.filename):
            filename = secure_filename(file.filename)
            filename,ext = os.path.splitext(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'example'+ext))
            session['example'] = (os.path.join(PATH, '_uploads'),'example'+ext)
            session['labels'] = None
            img=cv2.imread(os.path.join(*session['example']))
            r, jpg = cv2.imencode('.jpg', img)
            jpg_as_text = base64.b64encode(jpg)
            data=b'data:image/jpeg;base64,' + jpg_as_text
            data=data.decode("utf-8")

            return render_template('scale.html',edit_mode=True,mode='raw',title='Verify the scale of the software and of the example image is the same',z_values=SCALE['impedance'],colors=SCALE['colors'],example=data)
    return render_template('upload_file.html',what_to_upload=what_to_upload)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/_uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/scale')
@app.route('/scale/<filename>')
def scale_page(filename=''):
    return render_template('scale.html',edit_mode=False,title='Default Scale',z_values=SCALE['impedance'],colors=SCALE['colors'],example='')

@app.route('/default_example')
def default_example():
    session['example'] = (os.path.join(PATH,'static'),'default_example.bmp')
    with open(os.path.join(session['example'][0],'default_example.txt'), 'r') as f:
        session['labels'] = f.readlines()
    return render_template('scale.html',edit_mode=True,mode='default',title='This is the default example, verify the scale is correct.',z_values=SCALE['impedance'],colors=SCALE['colors'],example='default_example.bmp')

@app.route('/fill_labels')
def fill_labels():
    impedances = request.args.getlist('impedances')
    session['impedances']=[float(x) for x in impedances]
    #https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/40930153
    example = session['example'][1]
    folder = session['example'][0]
    example_electrodes = impedance.get_electrodes(os.path.join(folder,example))
    #frame = cv2.imdecode(example_electrodes[0][0], cv2.IMREAD_COLOR)
    #https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal
    #https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
    #session['example_electrodes'] = deepcopy(example_electrodes)  ndarrays are not json seriable
    encoded_electrodes=[]
    labels =[]
    for i,e in enumerate(example_electrodes):
        r, jpg = cv2.imencode('.jpg', e[0])
        jpg_as_text = base64.b64encode(jpg)
        data=b'data:image/jpeg;base64,' + jpg_as_text
        data=data.decode("utf-8")
        encoded_electrodes.append(data)
        labels.append('E'+str(i))
    if session['labels'] is None:
        session['labels'] = deepcopy(labels)
    #return show_message('heck')
    return render_template('fill_labels.html',electrodes=encoded_electrodes,labels=session['labels'])


@app.route('/upload_folder', methods=['POST', 'GET'])
def upload_folder():
    if request.method == 'POST':

        #print(request.files)
        if 'files[]' not in request.files:
            flash('No Files')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        filenames = []
        #https://stackoverflow.com/questions/5826286/how-do-i-use-google-chrome-11s-upload-folder-feature-in-my-own-code/5849341#5849341
        #https://stackoverflow.com/questions/3590058/does-html5-allow-drag-drop-upload-of-folders-or-a-folder-tree
        # Some comments say it wont get all the files?
        # https://stackoverflow.com/a/53058574
        # https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/50#files_and_directories
        # https://developer.mozilla.org/en-US/docs/Web/API/File/webkitRelativePath
        # https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory
        files = [f  for f in files if utils.is_valid_file(f.filename)]
        for file in files:
            if file :#and allowed_file(file.filename):
                    #accept files, since some eeg formats need sidecars...
                    #we could include all possible sidecar formats too but may mess up stuff
                    # keep like this for now
                #app.logger.info(file.__dict__)
                #useful when cannot debug https://stackoverflow.com/questions/2675028/list-attributes-of-an-object
                fileparts = utils.splitall(file.filename)
                filename = fileparts.pop()# filename is the last, after this fileparts wont have the filename
                filename = secure_filename(filename)
                rel_nested_dir = os.path.join(*fileparts)
                abs_nested_dir = os.path.join(app.config['UPLOAD_FOLDER'],'input',rel_nested_dir)
                os.makedirs(abs_nested_dir,exist_ok=True)
                file.save(os.path.join(abs_nested_dir, filename))
                filenames.append(os.path.join(rel_nested_dir,filename).replace('\\','/'))
        return render_template('exclude_files.html', filenames=filenames)

    else:
        #print(request)
        labels = request.args.getlist('labels')
        session['labels']=labels
        if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'],'input')):                           # Revisar si el directorio de salida ya existe
            shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'],'input'))                           # Limpiarlo en ese caso

        return render_template('upload_files.html')

@app.route("/init_process", methods=['POST', 'GET'])
def init_process():
    if request.method == 'POST':
        listOfFiles = utils._get_files(os.path.join(app.config['UPLOAD_FOLDER'],'input'))        # Lista de archivos a procesar
        if os.path.isdir(app.config['CONV_FOLDER']):                           # Revisar si el directorio de salida ya existe
            shutil.rmtree(app.config['CONV_FOLDER'])                           # Limpiarlo en ese caso
            os.makedirs(app.config['CONV_FOLDER'],exist_ok=True)
        example = session['example'][1]
        folder = session['example'][0]
        #print(folder,example)
        OUTPUT_DIR = app.config['CONV_FOLDER']
        EXAMPLE=os.path.join(folder,example)
        LABELS=session['labels']
        ROOT_DIR = os.path.join(app.config['UPLOAD_FOLDER'],'input')
        SAVE_IMAGES=True
        labeled_electrodes=impedance.process_example(EXAMPLE,LABELS,OUTPUT_DIR,SAVE_IMAGES)
        errors=[]
        for i,image in enumerate(listOfFiles):
            try:
                output = os.path.join(OUTPUT_DIR,os.path.split(image.replace(ROOT_DIR,''))[0].strip('/').strip('\\'))
                impedance.process_image(image,labeled_electrodes,output,SAVE_IMAGES,Z_VALUES=session['impedances'])
                print(i,image.replace(ROOT_DIR,''))
            except:
                errors.append({'file':image,'error':format_exc()})
                print('error',image.replace(ROOT_DIR,''))
        with open(os.path.join(OUTPUT_DIR,'errors.txt'), 'w') as outfile:
            json.dump(errors, outfile,indent=4)
        return render_template("ready.html")
    else:
        return render_template('init_processing.html')

@app.route("/exclude", methods=['POST', 'GET'])
def exclude():
    if request.method == "POST":

        filelist = utils._get_files(os.path.join(app.config['UPLOAD_FOLDER'],'input').replace('\\','/'))
        
        filelist = [x.replace('\\','/').replace(os.path.join(app.config['UPLOAD_FOLDER'],'input').replace('\\','/')+'/','') for x in filelist]
        #app.logger.info('filelist : {}'.format(filelist))
        #filelist = os.listdir(app.config['UPLOAD_FOLDER'])
        include = request.form.getlist('records')
        # for filename in filenames:
        #     if filename not in include:
        #         os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #filenames = os.listdir(app.config['UPLOAD_FOLDER'])
        #app.logger.info('include: {}'.format(include))

        filenames = [x for x in filelist if x in include]
        #app.logger.info('finalist : {}'.format(filenames))
        session['filelist']=filenames
        return render_template('files.html', filenames=filenames)
    else:
        return render_template('exclude_files.html')

import zipfile
from flask import send_file

def download_files(list_files,filename):
    zip_subdir = "archivos"
    #s = BytesIO()
    zf = zipfile.ZipFile(filename, "w")

    for fpath in list_files:
        zip_path = fpath.split("_convert\\")[-1]
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S.%f")
    name = f'converted_images_{timestampStr}.zip'
    #response = Response(s.getvalue(), content_type = "application/x-zip-compressed")
    #response['Content-Disposition'] = 'attachment; filename= "%s"' % filename

    # See https://stackoverflow.com/a/53390515/14068216
    #https://stackoverflow.com/questions/55519452/flask-send-file-is-sending-old-file-instead-of-newest/55519673
    response = send_file(filename, mimetype="application/x-zip-compressed", attachment_filename=name, as_attachment=True,cache_timeout=0)
    response.headers["x-filename"] = name
    response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    # # ..and correct content-disposition
    # response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return response

@app.route("/download", methods=["GET"])
def download():
    files = utils._get_files(app.config['CONV_FOLDER'],None)
    #print(files)
    return download_files(files,os.path.join(app.config['TEMP_FOLDER'],'the_zip.zip'))