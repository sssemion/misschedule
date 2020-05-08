import os

from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "secret_key_123")

from misschedule import controllers
from misschedule import jinja_filters
