from base64 import b64encode

import requests
from flask import render_template, make_response, session
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm, LoginForm
from misschedule.password_check import check_password, PasswordError


@app.route("/")
def index():
    token = session.get('token', None)
    if not token:
        return make_response(render_template('main-page.html'))
    headers = {"Authorization": f"Bearer {token}"}
    data = requests.get('http://127.0.0.1:5000/api/projects', headers=headers).json()
    print(data['projects'])
    return render_template('project-page.html', projects=data['projects'])


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password.render_kw["class"] = "input-str form-control is-invalid"
            form.password_again.render_kw["class"] = "input-str form-control is-invalid"
            return render_template('register.html', form=form, message="Пароли не совпадают")
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
        try:
            check_password(form.password.data)
        except PasswordError as e:
            form.password.render_kw["class"] = "input-str form-control is-invalid"
            form.password.errors.append(e)
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


@app.route('/project/<string:project_name>', methods=['GET', 'POST'])
def project_page(project_name):
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    project = requests.get(f'http://127.0.0.1:5000/api/users/get_project/{project_name}', headers=headers).json()
    print(project)
    if project.get('success', True):
        users = [requests.get(f'http://127.0.0.1:5000/api/users/{id}').json() for id in project['users']]
        tasks = requests.get(f'http://127.0.0.1:5000/api/projects/{int(project["project"]["id"])}/get_tasks').json()
        print(tasks)
        for item in range(len(tasks['tasks'])):
            user = requests.get(
                f'http://127.0.0.1:5000/api/users/{tasks["tasks"][item]["task"]["worker_id"]}').json()
            if user is not None:
                tasks['tasks'][item]['task']['worker_id'] = user['username']
        chats = requests.get(f'http://127.0.0.1:5000/api/projects/{int(project["project"]["id"])}/get_chats').json()
        return render_template('project-main-page.html', project=project["project"], users=users, tasks=tasks,
                               chats=chats)
    return redirect('/')
