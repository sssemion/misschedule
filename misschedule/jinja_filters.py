import datetime

import requests
from flask import session

from misschedule import app


# Фильтры в шаблонах
def time_to_deadline(date, duration):
    now = datetime.datetime.now()
    deadline = datetime.datetime.fromisoformat(date) + datetime.timedelta(seconds=duration)
    if now > deadline:
        return -1
    return int((deadline - now).total_seconds())


def project_title_by_id(project_id):
    token = session.get('token', None)
    if token is None:
        return ""

    headers = {"Authorization": f"Bearer {token}"}
    project = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}', headers=headers).json()
    return project["project"]["title"]


def transparentize(color, value):
    rgb = [str(int(color[i:i+2], 16)) for i in (1, 3, 5)]
    return f"rgba({', '.join(rgb)}, {1 - value})"


app.jinja_env.filters['time_to_deadline'] = time_to_deadline
app.jinja_env.filters['project_title_by_id'] = project_title_by_id
app.jinja_env.filters['transparentize'] = transparentize
