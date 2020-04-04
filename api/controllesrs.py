from flask import request, jsonify
from flask_restful import abort

from api import app
from api.data import db_session
from api.data.project import Project
from api.data.user import User


def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    if not project:
        abort(404, message=f"Project {project_id} not found")


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


@app.route("/api/projects/<int:project_id>/add_user/<int:user_id>", methods=['POST'])
def add_user_to_project(project_id, user_id):
    abort_if_project_not_found(project_id)
    abort_if_user_not_found(user_id)

    session = db_session.create_session()
    project = session.query(Project).get(project_id)
    user = session.query(User).get(user_id)
    if user.id not in list(map(lambda x: x.id, project.users)):
        project.users.append(user)
    session.commit()
    return jsonify({'success': True})


@app.route('/api/projects/<int:project_id>/add_user/', methods=['POST'])
def add_users_to_project(project_id):

    try:
        user_ids = list(map(lambda x: int(x), list(request.form.getlist('id'))))
    except ValueError:
        abort(400, message=f"Один или несколько id пользователей некорректны")

    abort_if_project_not_found(project_id)
    for user_id in user_ids:
        abort_if_user_not_found(user_id)

    session = db_session.create_session()
    project = session.query(Project).get(project_id)

    for user_id in user_ids:
        user = session.query(User).get(user_id)
        if user.id not in list(map(lambda x: x.id, project.users)):
            project.users.append(user)
    session.commit()
    return jsonify({'success': True})
