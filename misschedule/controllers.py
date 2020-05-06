import datetime
from base64 import b64encode

import requests
from flask import render_template, make_response, session, request, jsonify
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm, LoginForm, ProjectForm, TaskForm
from misschedule.jinja_filters import user_by_id
from misschedule.password_check import check_password, PasswordError


@app.route("/")
def index():
    token = session.get('token', None)
    if not token:
        return make_response(render_template('main-page.html'))

    headers = {"Authorization": f"Bearer {token}"}
    projects = requests.get('http://127.0.0.1:5000/api/projects', headers=headers)
    projects_data = projects.json()
    tasks = requests.get('http://127.0.0.1:5000/api/tasks', headers=headers)
    tasks_data = tasks.json()

    if not (projects.status_code == tasks.status_code == 200):
        if projects.status_code == 401 or tasks.status_code == 401:  # Unauthorized
            return redirect("/login")
            # TODO:  Оповещение о том, что время сессии истекло

    return render_template('project-page.html', projects=projects_data['projects'], tasks=tasks_data['tasks'])


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password.render_kw["class"] = "input-str form-control is-invalid"
            form.password_again.render_kw["class"] = "input-str form-control is-invalid"
            return render_template('register.html', form=form, message="Пароли не совпадают")

        try:
            check_password(form.password.data)
        except PasswordError as e:
            form.password.render_kw["class"] = "input-str form-control is-invalid"
            form.password.errors.append(e)
            return render_template('register.html', form=form)

        response = requests.post('http://127.0.0.1:5000/api/users', {
            'username': form.username.data,
            'email': form.email.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'password': form.password.data
        })

        data = response.json()
        if data['success']:
            session['token'] = data['authToken']['token']
            return redirect('/')
        if response.status_code == 400:
            if f"User {form.username.data} " in data.get('message', ''):
                form.username.render_kw["class"] = "input-str form-control is-invalid"
                form.username.errors.append('Имя уже занято')
            if f"email {form.email.data} " in data.get('message', ''):
                form.email.render_kw["class"] = "input-str form-control is-invalid"
                form.email.errors.append('Email уже занят')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_and_pass = b64encode(bytes(f"{form.email.data}:{form.password.data}".encode('utf-8'))).decode("ascii")
        headers = {'Authorization': f'Basic {user_and_pass}'}
        request = requests.post('http://127.0.0.1:5000/api/login', headers=headers).json()
        if not request['success']:
            return render_template('login.html', form=form, login_failed=True)
        session['token'] = request['authToken']['token']
        return redirect('/')
    return render_template('login.html', form=form)


@app.route('/project', methods=['GET', 'POST'])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            token = session['token']
            headers = {"Authorization": f"Bearer {token}"}
            data = requests.post('http://127.0.0.1:5000/api/projects',
                                 {'project_name': form.project_name.data, 'title': form.title.data,
                                  'description': form.description.data},
                                 headers=headers).json()
            if data['success']:
                return redirect('/')
        except:
            return render_template('create-project.html', form=form)
    return render_template('create-project.html', form=form)


@app.route('/projects/<string:project_name>', methods=['GET', 'POST'])
def project_page(project_name):
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    project = requests.get(f'http://127.0.0.1:5000/api/users/get_project/{project_name}', headers=headers).json()
    if project.get('success', True):
        users = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_users', headers=headers).json()

        form = TaskForm(users=users["users"])
        task_already_exists = False
        start_with_form = False
        if form.validate_on_submit():
            params = {
                "project_id": project["project"]["id"],
                "title": form.title.data,
                "description": form.description.data,
                "duration": (form.deadline.data - datetime.datetime.now()).total_seconds(),
                "worker_id": int(form.worker.data),
                "tag": form.tag.data,
                "color": form.color_field.data,
                "condition": 0,
            }
            response = requests.post("http://127.0.0.1:5000/api/tasks", headers=headers, json=params)
            response_data = response.json()
            if response.status_code == 400 and response_data.get("message", '').startswith("Task with title '"):
                task_already_exists = True
                start_with_form = True

        team_leader = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_team_leader', headers=headers).json()
        tasks = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_tasks', headers=headers).json()
        chats = requests.get(f'http://127.0.0.1:5000/api/projects/{int(project["project"]["id"])}/get_chats', headers=headers).json()

        return render_template('project-main-page.html', project=project["project"], users=users["users"], tasks=tasks["tasks"],
                               chats=chats["chats"], team_leader=team_leader, form=form,
                               task_already_exists=task_already_exists, start_with_form=start_with_form)
    return redirect('/')


#
# AJAX-запросы
#


@app.route('/ajax/complete_item', methods=['POST'])
def complete_item():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = {"success": True}
    for item_id in data["item_ids"]:
        r = requests.post(f'http://127.0.0.1:5000/api/tasks/{data["task_id"]}/complete_item/{item_id}', headers=headers).json()
    try:
        r["completed_by"] = user_by_id(r["completed_by_id"])
    except KeyError:
        pass
    return jsonify(r)


@app.route("/ajax/set_task_condition", methods=['POST'])
def set_task_condition():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f'http://127.0.0.1:5000/api/tasks/{data["task_id"]}/set_condition/{data.get("condition", -1)}', headers=headers).json()
    return jsonify(r)
