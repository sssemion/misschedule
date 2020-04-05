from flask import request, jsonify
from flask_restful import abort

from api import app
from api.data import db_session
from api.data.chat import Chat
from api.data.project import Project
from api.data.user import User


def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    return project


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")
    return user


def abort_if_chat_not_found(chat_id):
    session = db_session.create_session()
    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"User {chat_id} not found")
    return chat


@app.route("/api/projects/<int:project_id>/add_user/<int:user_id>", methods=['POST'])
def add_user_to_project(project_id, user_id):
    project = abort_if_project_not_found(project_id)
    user = abort_if_user_not_found(user_id)

    session = db_session.create_session()

    if user.id not in list(map(lambda x: x.id, project.users)):
        project.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/projects/<int:project_id>/add_user/', methods=['POST'])
def add_users_to_project(project_id):
    project = abort_if_project_not_found(project_id)
    users = list(map(lambda x: abort_if_user_not_found(x), list(request.form.getlist('id'))))

    session = db_session.create_session()

    for user in users:
        if user.id not in list(map(lambda x: x.id, project.users)):
            project.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/chats/<int:chat_id>/add_user/<int:user_id>', methods=['POST'])
def add_user_to_chat(chat_id, user_id):
    chat = abort_if_chat_not_found(chat_id)
    user = abort_if_user_not_found(user_id)

    session = db_session.create_session()

    if user.id not in list(map(lambda x: x.id, chat.users)):
        chat.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/chats/<int:chat_id>/add_user/', methods=['POST'])
def add_users_to_chat(chat_id):
    chat = abort_if_chat_not_found(chat_id)
    users = list(map(lambda x: abort_if_user_not_found(x), list(request.form.getlist('id'))))

    session = db_session.create_session()

    for user in users:
        if user.id not in list(map(lambda x: x.id, chat.users)):
            chat.users.append(user)

    session.commit()
    return jsonify({'success': True})
