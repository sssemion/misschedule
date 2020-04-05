from flask import request, jsonify
from flask_restful import abort

from api import app
from api.data import db_session
from api.data.chat import Chat
from api.data.project import Project
from api.data.user import User


@app.route("/api/projects/<int:project_id>/add_user/<int:user_id>", methods=['POST'])
def add_user_to_project(project_id, user_id):
    session = db_session.create_session()

    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

    if user.id not in list(map(lambda x: x.id, project.users)):
        project.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/projects/<int:project_id>/add_user/', methods=['POST'])
def add_users_to_project(project_id):
    session = db_session.create_session()

    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")

    for user_id in request.form.getlist('id'):
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        if user_id not in list(map(lambda x: x.id, project.users)):
            project.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/chats/<int:chat_id>/add_user/<int:user_id>', methods=['POST'])
def add_user_to_chat(chat_id, user_id):
    session = db_session.create_session()

    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"Chat {chat_id} not found")
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

    if user.id not in list(map(lambda x: x.id, chat.users)):
        chat.users.append(user)

    session.commit()
    return jsonify({'success': True})


@app.route('/api/chats/<int:chat_id>/add_user/', methods=['POST'])
def add_users_to_chat(chat_id):
    session = db_session.create_session()

    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f"Chat {chat_id} not found")
    for user_id in request.form.getlist('id'):
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        if user_id not in list(map(lambda x: x.id, chat.users)):
            chat.users.append(user)

    session.commit()
    return jsonify({'success': True})
