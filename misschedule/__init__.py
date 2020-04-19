from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# TODO: генерация нормального ключа

from misschedule import controllers
from misschedule import jinja_filters
