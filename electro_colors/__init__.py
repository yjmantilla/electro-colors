from flask import Flask

app = Flask(__name__)
from electro_colors.config import Config
app.config.from_object(Config)

from electro_colors import routes