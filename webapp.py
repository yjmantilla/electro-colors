"""Open browser in incognito mode to avoid cache problems."""
from zcolors import app

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=True,threaded=True) # Se inicializa el servicio a través del puerto 5000