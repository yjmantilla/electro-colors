from flask import Flask

app = Flask(__name__)
from zcolors.config import Config
app.config.from_object(Config)

from zcolors import routes