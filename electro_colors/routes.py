from electro_colors import app, config
from electro_colors import impedance
import os
from flask import render_template,flash,redirect,request,url_for
from werkzeug.utils import secure_filename

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))

def load_files():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files.get('file')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','bmp'}

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
            return render_template('scale.html',z_values=SCALE['impedance'],colors=SCALE['colors'],example=os.path.split(app.config['UPLOAD_FOLDER'])[-1] +'/'+'example'+ext)
    return render_template('upload_file.html',what_to_upload=what_to_upload)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/scale')
@app.route('/scale/<filename>')
def scale_page(filename=''):
    return render_template('scale.html',z_values=SCALE['impedance'],colors=SCALE['colors'],example='')
