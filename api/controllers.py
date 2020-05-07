import datetime
import json

from flask import request, jsonify, g
from flask_restful import abort
from werkzeug.exceptions import HTTPException

from api import app
from api.auth import basic_auth, token_auth
from api.data import db_session
from api.data.chat import Chat
from api.data.project import Project
from api.data.task import Task
from api.data.task_item import TaskItem
from api.data.user import User


@app.route('/api/login', methods=['POST'])
@basic_auth.login_required
# Путь получает в заголовках запроса логин и пароль пользователя (декоратор @basic.auth.login_required)
# и, если данные верны, возвращает токен. Чтобы защитить маршруты API с помощью токенов, необходимо
# добавить декоратор @token_auth.login_required
def get_token():
    token = g.current_user.get_token()
    g.db_session.commit()
    return jsonify({'success': True, 'authToken': {'token': token,
                                                   'expires': str(g.current_user.token_expiration)}})


@app.route('/api/logout', methods=['POST'])
@token_auth.login_required
# Отзыв токена
def revoke_token():
    g.current_user.revoke_token()
    g.db_session.commit()
    g.current_user = None
    g.db_session = None
    return jsonify({'success': True})


@app.errorhandler(HTTPException)
def error(e):
    response = e.get_response()
    params = {
        'success': False,
    }
    try:
        for key, value in e.data.items():
            params[key] = value
    except AttributeError:
        pass
    response.data = json.dumps(params)
    response.content_type = "application/json"
    return response


@app.route("/api/projects/<int:project_id>/add_user/<int:user_id>", methods=['POST'])
@token_auth.login_required
def add_user_to_project(project_id, user_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project.team_leader != g.current_user:
        abort(403)
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

    if user.id not in list(map(lambda x: x.id, project.users)):
        project.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/projects/<int:project_id>/add_user', methods=['POST'])
@token_auth.login_required
def add_users_to_project(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project.team_leader != g.current_user:
        abort(403)

    added_users = []
    for user_id in request.form.getlist('id'):
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        if int(user_id) not in list(map(lambda x: x.id, project.users)):
            project.users.append(user)
            added_users.append(user)

    session.commit()
    return jsonify({'success': True, "users": [
        user.to_dict(only=('id', 'email', 'username', 'first_name', 'last_name'))
                    for user in added_users]})


@app.route('/api/chats/<int:chat_id>/add_user/<int:user_id>', methods=['POST'])
@token_auth.login_required
def add_user_to_chat(chat_id, user_id):
    session = db_session.create_session()

    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"Chat {chat_id} not found")
    if chat.project.team_leader != g.current_user:
        abort(403)
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

    if user_id not in list(map(lambda x: x.id, chat.users)):
        if user_id in list(map(lambda x: x.id, chat.project.users)):
            chat.users.append(user)
        else:
            abort(400, message=f"User {user_id} is not in chat's project")

    session.commit()
    return jsonify({'success': True})


@app.route('/api/chats/<int:chat_id>/add_user', methods=['POST'])
@token_auth.login_required
def add_users_to_chat(chat_id):
    session = db_session.create_session()

    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"Chat {chat_id} not found")
    if chat.project.team_leader != g.current_user:
        abort(403)
    project_users_ids = list(map(lambda x: x.id, chat.project.users))

    for user_id in request.form.getlist('id'):
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        user_id = int(user_id)
        if user_id not in list(map(lambda x: x.id, chat.users)):
            if user_id in project_users_ids:
                chat.users.append(user)
            else:
                abort(400, message=f"User {user_id} is not in chat's project")

    session.commit()
    return jsonify({'success': True})


@app.route('/api/tasks/<int:task_id>/complete_item/<int:item_id>', methods=['POST'])
@token_auth.login_required
def set_task_items(task_id, item_id):
    session = db_session.create_session()

    task = session.query(Task).get(task_id)
    item = session.query(TaskItem).get(item_id)
    if not task:
        abort(404, message=f"Task {task_id} not found")
    if not item or item not in task.items:
        abort(404, messsage=f"TaskItem {item_id} not found")
    if not (g.current_user == task.worker or g.current_user == task.creator):
        abort(403)
    item.completed = True
    item.completed_by_id = g.current_user.id
    item.completion_date = datetime.datetime.now()
    session.commit()
    return jsonify({'success': True, "completed_by_id": item.completed_by_id,
                    "completion_date": ':'.join(str(item.completion_date.replace(microsecond=0)).split(':')[:-1])})


@app.route('/api/tasks/<int:task_id>/set_condition/<int:condition>', methods=['POST'])
@token_auth.login_required
def set_task_condition(task_id, condition):
    session = db_session.create_session()

    task = session.query(Task).get(task_id)
    if not task:
        abort(404, message=f"Task {task_id} not found")
    if not (g.current_user == task.worker or g.current_user == task.creator):
        abort(403)
    if condition not in (0, 1, 2):
        abort(400, message=f"Condition must be one of (0, 1, 2)")
    task.condition = condition
    session.commit()
    return jsonify({'success': True, 'condition': condition})


@app.route('/api/users/get_project/<string:project_name>', methods=['GET'])
@token_auth.login_required
def get_project(project_name):
    user = g.current_user
    project = user.projects[list(map(lambda p: p.project_name, user.projects)).index(project_name)]
    return jsonify({
        'project': project.to_dict(only=('id', 'team_leader_id', 'project_name', 'title', 'description', 'reg_date')),
        'users': [item.id for item in project.users]})


@app.route('/api/users/get_user_by_name/<string:username>', methods=['GET'])
def get_user_by_name(username):
    session = db_session.create_session()
    user = session.query(User).filter(User.username == username).first()
    return jsonify({
        'user': user.to_dict(only=('id', 'email', 'username', 'first_name', 'last_name', 'reg_date')),
        'projects': [
            {
                'project':
                    project.to_dict(only=('project_name', 'title', 'description', 'team_leader_id')),
                'team_leader': project.team_leader.to_dict(only=('id', 'username', 'first_name', 'last_name'))
            }
            for project in user.projects]
    })


@app.route('/api/users/get_myself')
@token_auth.login_required
def get_myself():
    user = g.current_user
    return jsonify({'user': user.to_dict(
        only=('id', 'email', 'username', 'first_name', 'last_name', 'reg_date'))})


@app.route('/api/users/<username>/<project_name>')
def get_username_project(username, project_name):
    session = db_session.create_session()
    user = session.query(User).filter(User.username == username).first()
    project = user.projects[list(map(lambda p: p.project_name, user.projects)).index(project_name)]
    return jsonify({
        'project': project.to_dict(only=('id', 'team_leader_id', 'project_name', 'title', 'description', 'reg_date')),
        'users': [item.id for item in project.users]})


@app.route('/api/chats/<int:chat_id>/get_messages')
@token_auth.login_required
def get_chat_messages(chat_id):
    session = db_session.create_session()
    chat = session.query(Chat).get(chat_id)
    messages = chat.messages
    messages = sorted(messages, key=lambda x: x.date)
    return jsonify({
        'messages': [
            {'message': message.to_dict(only=('chat_id', 'user_id', 'message', 'date')),
             'user': message.user.to_dict(only=('id', 'username', 'email', 'first_name', 'last_name'))}
            for message in messages],
    })


@app.route('/api/projects/<int:project_id>/get_tasks')
@token_auth.login_required
def get_project_tasks(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project not in g.current_user.projects:
        abort(403)
    tasks = project.tasks
    return jsonify(
        {'tasks': [
            {
                'task': task.to_dict(only=(
                    "id", "project_id", "title", "description", "duration", "worker_id", "creator_id",
                    "tag", "color", "condition", "image", "date")),
                'items': [item.to_dict(
                    only=("id", "title", "description", "completed", "completed_by_id", "completion_date")) for
                    item in task.items],
                'canYouEdit': g.current_user == task.worker or g.current_user == task.creator,
            } for task in tasks]})


@app.route('/api/projects/<int:project_id>/get_chats')
@token_auth.login_required
def get_project_chats(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project not in g.current_user.projects:
        abort(403)
    chats = project.chats
    return jsonify(
        {'chats': [
            {
                'chat': chat.to_dict(only=('id', 'title', 'project_id', 'reg_date')),
                'users': [item.id for item in chat.users]
            } for chat in chats]})


@app.route('/api/projects/<int:project_id>/get_users')
@token_auth.login_required
def get_project_users(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project not in g.current_user.projects:
        abort(403)
    users = project.users
    return jsonify(
        {'users': [user.to_dict(only=('id', 'email', 'username', 'first_name', 'last_name', 'reg_date'))
                   for user in users]})


@app.route('/api/projects/<int:project_id>/get_team_leader')
@token_auth.login_required
def get_project_team_leader(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    if project not in g.current_user.projects:
        abort(403)
    return jsonify(project.team_leader.to_dict(only=('id', 'email', 'username', 'first_name', 'last_name', 'reg_date')))


@app.route('/api/users/search/<username>')
def search_user_by_username(username):
    session = db_session.create_session()
    users = session.query(User).filter(User.username.ilike(f"%{username}%"))
    if request.args.get("project_id", False):
        project = session.query(Project).get(request.args.get("project_id"))
        users = users.filter(User.id.notin_(list(map(lambda x: x.id, project.users))))
    users = users.all()

    return jsonify({"success": True, "users": [
        user.to_dict(only=('id', 'email', 'username', 'first_name', 'last_name')) for user in users],
                    'found': len(users)
                })
