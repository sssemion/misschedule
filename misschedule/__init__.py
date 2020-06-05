import os

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "secret_key_123")
app.config['API_SERVER_NAME'] = 'http://127.0.0.1:5000'

from misschedule import controllers
from misschedule import jinja_filters
