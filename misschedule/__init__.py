import base64
import os

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = base64.b64encode(os.urandom(24)).decode("utf-8")

from misschedule import controllers
from misschedule import jinja_filters
