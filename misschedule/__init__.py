from flask import Flask

app = Flask(__name__)

from misschedule import controllers
