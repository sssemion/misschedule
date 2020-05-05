from base64 import b64encode

import requests
from flask import render_template, make_response, session
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm, LoginForm, ProjectForm
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


@app.route('/<string:username>/<string:project_name>', methods=['GET', 'POST'])
def project_page(username, project_name):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    project = requests.get(f'http://127.0.0.1:5000/api/users/{username}/{project_name}', headers=headers).json()
    if project.get('success', True):
        users = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_users',
                             headers=headers).json()
        team_leader = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_team_leader',
                                   headers=headers).json()
        tasks = requests.get(f'http://127.0.0.1:5000/api/projects/{project["project"]["id"]}/get_tasks',
                             headers=headers).json()
        # for item in range(len(tasks['tasks'])):
        #     user = requests.get(
        #         f'http://127.0.0.1:5000/api/users/{tasks["tasks"][item]["task"]["worker_id"]}')
        #     user = user.json()['user']
        #     if user.get('success', True):
        #         tasks['tasks'][item]['task']['worker_id'] = user['username']
        chats = requests.get(f'http://127.0.0.1:5000/api/projects/{int(project["project"]["id"])}/get_chats',
                             headers=headers).json()
        return render_template('project-main-page.html', project=project["project"], users=users["users"],
                               tasks=tasks["tasks"],
                               chats=chats["chats"], team_leader=team_leader)
    return redirect('/')


@app.route('/chat/<int:chat_id>')
def chat_page(chat_id):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    chat = requests.get(f'http://127.0.0.1:5000/api/chats/{chat_id}', headers=headers).json()
    messages = requests.get(f'http://127.0.0.1:5000/api/chats/{chat_id}/get_messages', headers=headers).json()
    return render_template('chat-page.html', messages=messages, chat=chat)


@app.route('/users/<string:username>')
def user_page(username):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    request = requests.get(f'http://127.0.0.1:5000/api/users/get_user_by_name/{username}', headers=headers).json()
    user, projects = request['user'], request['projects']
    return render_template('user-page.html', user=user, projects=projects)
