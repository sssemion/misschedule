from flask import send_from_directory

from misschedule import app


@app.route("/")
def index():
    return send_from_directory('static/html', 'index.html')
