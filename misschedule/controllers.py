import datetime
from base64 import b64encode

import requests
from flask import render_template, make_response, session, request, jsonify
from werkzeug.exceptions import abort, HTTPException
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm, LoginForm, ProjectForm, TaskForm, AddUserForm
from misschedule.jinja_filters import user_by_id, project_by_id
from misschedule.password_check import check_password, PasswordError


# Функция-обертка над функцией request_get(), которая вызывает исключение, если пользователь не авторизован
def request_get(*args, **kwargs):
    r = requests.get(*args, **kwargs)
    if r.status_code == 401:
        abort(401)
    if r.status_code == 403:
        abort(403)
    if r.status_code == 404:
        abort(404)
    return r


# Функция-обертка над функцией request_post(), которая вызывает исключение, если пользователь не авторизован
def request_post(*args, **kwargs):
    r = requests.post(*args, **kwargs)
    if r.status_code == 401:
        abort(401)
    if r.status_code == 403:
        abort(403)
    if r.status_code == 404:
        abort(404)
    return r


@app.errorhandler(401)
def unauthorized(*args, **kwargs):
    session.pop("token", None)
    return redirect("/")


@app.errorhandler(403)
def no_rights(*args, **kwargs):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]
    except HTTPException:
        myself = {}
    return render_template('error.html', ertype=403, message='Нет прав', myself=myself)


@app.errorhandler(404)
def not_found(*args, **kwargs):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]
    except HTTPException:
        myself = {}
    return render_template('error.html', ertype=404, messgae='Не найдено', myself=myself)


@app.route("/")
def index():
    token = session.get('token', None)
    if not token:
        return make_response(render_template('main-page.html'))

    headers = {"Authorization": f"Bearer {token}"}
    projects = request_get(f'{app.config["API_SERVER_NAME"]}/api/projects', headers=headers)
    projects_data = projects.json()
    tasks = request_get(f'{app.config["API_SERVER_NAME"]}/api/tasks', headers=headers)
    tasks_data = tasks.json()
    myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]

    if not (projects.status_code == tasks.status_code == 200):
        if projects.status_code == 401 or tasks.status_code == 401:  # Unauthorized
            return make_response(render_template('main-page.html'))

    return render_template('project-page.html', projects=projects_data['projects'], tasks=tasks_data['tasks'],
                           myself=myself)


@app.route('/signup', methods=['GET', 'POST'])
def register():
    token = session.get('token', None)
    if token:
        return redirect('/')
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

        response = request_post(f'{app.config["API_SERVER_NAME"]}/api/users', {
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
    token = session.get('token', None)
    if token:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user_and_pass = b64encode(bytes(f"{form.email.data}:{form.password.data}".encode('utf-8'))).decode("ascii")
        headers = {'Authorization': f'Basic {user_and_pass}'}
        request = requests.post(f'{app.config["API_SERVER_NAME"]}/api/login', headers=headers).json()
        if not request['success']:
            return render_template('login.html', form=form, login_failed=True)
        session['token'] = request['authToken']['token']
        return redirect('/')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    headers = {'Authorization': f'Bearer {session.get("token", "")}'}
    request = request_post(f'{app.config["API_SERVER_NAME"]}/api/logout', headers=headers).json()
    session.pop("token", None)
    return redirect('/')


@app.route('/project', methods=['GET', 'POST'])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        token = session.get('token', '')
        headers = {"Authorization": f"Bearer {token}"}
        data = request_post(f'{app.config["API_SERVER_NAME"]}/api/projects', {
            'project_name': form.project_name.data, 'title': form.title.data,
            'description': form.description.data}, headers=headers).json()
        if data['success']:
            return redirect('/')
        else:
            if data["message"].startswith("Project with name"):
                form.project_name.render_kw["class"] = "input-str form-control is-invalid"
                form.project_name.errors.append("Проект с таким именем уже существует")
    headers = {"Authorization": f"Bearer {session.get('token', '')}"}
    myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]
    return render_template('create-project.html', form=form, myself=myself)


@app.route('/<string:username>/<string:project_name>', methods=['GET', 'POST'])
def project_page(username, project_name):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    project = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/{username}/{project_name}', headers=headers).json()
    if project.get('success', True):
        users = request_get(f'{app.config["API_SERVER_NAME"]}/api/projects/{project["project"]["id"]}/get_users',
                            headers=headers).json()

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
            response = request_post(f'{app.config["API_SERVER_NAME"]}/api/tasks', headers=headers, json=params)
            response_data = response.json()
            if response.status_code == 400 and response_data.get("message", '').startswith("Task with title '"):
                task_already_exists = True
                start_with_form = True
            elif response.status_code == 200 and response_data.get("success", False):
                return redirect(f"/{username}/{project_name}")

        team_leader = request_get(f'{app.config["API_SERVER_NAME"]}/api/projects/{project["project"]["id"]}/get_team_leader',
                                  headers=headers).json()
        tasks = request_get(f'{app.config["API_SERVER_NAME"]}/api/projects/{project["project"]["id"]}/get_tasks',
                            headers=headers).json()
        chats = request_get(f'{app.config["API_SERVER_NAME"]}/api/projects/{int(project["project"]["id"])}/get_chats',
                            headers=headers).json()
        myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]

        return render_template('project-main-page.html', project=project["project"], users=users["users"],
                               tasks=tasks["tasks"],
                               chats=chats["chats"], team_leader=team_leader, form=form, myself=myself,
                               task_already_exists=task_already_exists, start_with_form=start_with_form)
    return redirect('/')


@app.route('/chat/<int:chat_id>', methods=["GET", "POST"])
def chat_page(chat_id):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    chat = request_get(f'{app.config["API_SERVER_NAME"]}/api/chats/{chat_id}', headers=headers).json()
    project = project_by_id(chat["chat"]["project_id"])
    user_ids = list(map(lambda x: x["id"], chat["users"]))
    form = AddUserForm(filter(lambda x: x["id"] not in user_ids, project["users"]))
    if form.validate_on_submit():
        params = {"id": list(map(int, form.users.data))}
        request_post(f'{app.config["API_SERVER_NAME"]}/api/chats/{chat_id}/add_user', headers=headers, data=params)
        return redirect(f"/chat/{chat_id}")
    messages = request_get(f'{app.config["API_SERVER_NAME"]}/api/chats/{chat_id}/get_messages', headers=headers).json()
    myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]
    return render_template('chat-page.html', messages=messages, chat=chat, project=project, form=form,
                           myself=myself)


@app.route('/users/<string:username>')
def user_page(username):
    token = session.get('token', None)
    headers = {"Authorization": f"Bearer {token}"}
    response = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_user_by_name/{username}', headers=headers).json()
    user, projects = response['user'], response['projects']
    try:
        myself = request_get(f'{app.config["API_SERVER_NAME"]}/api/users/get_myself', headers=headers).json()["user"]
    except HTTPException:
        myself = {}
    return render_template('user-page.html', user=user, projects=projects, myself=myself)


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
        r = request_post(f'{app.config["API_SERVER_NAME"]}/api/tasks/{data["task_id"]}/complete_item/{item_id}',
                         headers=headers).json()
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
    r = requests.post(f'{app.config["API_SERVER_NAME"]}/api/tasks/{data["task_id"]}/set_condition/{data.get("condition", -1)}',
                      headers=headers).json()
    return jsonify(r)


@app.route('/ajax/send_message', methods=["POST"])
def send_message():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f'{app.config["API_SERVER_NAME"]}/api/messages', headers=headers, json=data).json()
    return jsonify(r)


@app.route('/ajax/create_chat', methods=["POST"])
def create_chat():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f'{app.config["API_SERVER_NAME"]}/api/chats', headers=headers, json=data).json()
    return jsonify(r)


@app.route('/ajax/create_task_items', methods=["POST"])
def create_task_items():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    response = {'items': []}
    for item in data["items"]:
        r = requests.post(f'{app.config["API_SERVER_NAME"]}/api/task_items', headers=headers, json=item)
        response["items"].append(r.json())
    return jsonify(response)


@app.route('/ajax/search_users', methods=["POST"])
def search_users():
    data = request.get_json()
    r = requests.get(f'{app.config["API_SERVER_NAME"]}/api/users/search/{data["username"]}',
                     params={"project_id": data["project_id"]}).json()
    return jsonify(r)


@app.route('/ajax/add_users_to_project', methods=["POST"])
def add_users_to_project():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f'{app.config["API_SERVER_NAME"]}/api/projects/{data["project_id"]}/add_user',
                      headers=headers, data={'id': data['users']}).json()
    return r


@app.route('/ajax/check_for_new_messages', methods=["POST"])
def check_for_new_messages():
    token = session.get("token")
    data = request.get_json()
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f'{app.config["API_SERVER_NAME"]}/api/chats/{data["chat_id"]}/get_messages',
                     params={"last_message_id": data["last_message_id"]},
                     headers=headers).json()
    return jsonify({
        "length": len(r.get("messages", [])),
        **r
    })
