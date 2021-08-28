from copy import deepcopy
from zcolors import app, config
from zcolors import impedance
from zcolors import __path__ as PATH
PATH = PATH[0]
import os
from flask import render_template,flash,redirect,request,url_for,session
from werkzeug.utils import secure_filename
from traceback import format_exc
import cv2
import base64

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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','bmp'}

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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename,ext = os.path.splitext(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'example'+ext))
            session['example'] = (os.path.join(PATH,'static', '_uploads'),'example'+ext)
            session['labels'] = None
            return render_template('scale_button.html',title='Verify the scale of the software and of the example image is the same',z_values=SCALE['impedance'],colors=SCALE['colors'],example=os.path.split(app.config['UPLOAD_FOLDER'])[-1] +'/'+'example'+ext)
    return render_template('upload_file.html',what_to_upload=what_to_upload)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/scale')
@app.route('/scale/<filename>')
def scale_page(filename=''):
    return render_template('scale.html',title='Default Scale',z_values=SCALE['impedance'],colors=SCALE['colors'],example='')

@app.route('/default_example')
def default_example():
    session['example'] = (os.path.join(PATH,'static'),'default_example.bmp')
    with open(os.path.join(session['example'][0],'default_example.txt'), 'r') as f:
        session['labels'] = f.readlines()
    return render_template('scale_button.html',title='This is the default example, verify the scale is correct.',z_values=SCALE['impedance'],colors=SCALE['colors'],example='default_example.bmp')

@app.route('/fill_labels')
def fill_labels():
    #https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/40930153
    example = session['example'][1]
    folder = session['example'][0]
    example_electrodes = impedance.get_electrodes(example,folder)
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
