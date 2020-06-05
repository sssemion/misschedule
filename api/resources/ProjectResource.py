import datetime

from flask import jsonify, g
from flask_restful import abort, Resource

from api.auth import token_auth
from api.data import db_session
from api.resources.parsers import project_parser_for_adding, project_parser_for_updating
from api.data.project import Project


def abort_if_project_not_found(func):
    def new_func(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if not project:
            abort(404, success=False, message=f"Project {project_id} not found")
        return func(self, project_id)

    return new_func


def check_if_user_is_a_member(func):
    def new_func(self, project_id):
        if project_id not in map(lambda x: x.id, g.current_user.projects):
            abort(403, success=False)
        return func(self, project_id)

    return new_func


class ProjectResource(Resource):
    @abort_if_project_not_found
    @token_auth.login_required
    @check_if_user_is_a_member
    def get(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if project not in g.current_user.projects:
            abort(403, success=False)
        return jsonify({
            'project': project.to_dict_myself(),
            'team_leader': project.team_leader.to_dict_myself(),
            'users': [user.to_dict_myself()
                      for user in project.users]})

    @abort_if_project_not_found
    @token_auth.login_required
    def delete(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if project.team_leader != g.current_user:
            abort(403, success=False)
        session.delete(project)
        session.commit()
        return jsonify({'success': True})

    @abort_if_project_not_found
    @token_auth.login_required
    def put(self, project_id):
        args = project_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос 
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if project.team_leader != g.current_user:
            abort(403, success=False)
        if 'project_name' in args and args['project_name'] in map(lambda x: x.project_name, g.current_user.projects):
            abort(400, success=False, message=f"Project with name '{args['project_name']}' already exists")
        for key, value in args.items():
            if value is not None:
                exec(f"project.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class ProjectListResource(Resource):
    @token_auth.login_required
    def get(self):
        return jsonify({
            'projects': [
                {
                    'project': project.to_dict_myself(),
                    'team_leader': project.team_leader.to_dict_myself(),
                    'users': [user.to_dict_myself()
                              for user in project.users]
                }
                for project in g.current_user.projects],
        })

    @token_auth.login_required
    def post(self):
        args = project_parser_for_adding.parse_args(strict=True)
        if args['project_name'] in map(lambda x: x.project_name, g.current_user.projects):
            abort(400, success=False, message=f"Project with name '{args['project_name']}' already exists")
        project = Project(
            team_leader_id=g.current_user.id,
            project_name=args['project_name'],
            title=args['title'],
            description=args['description'],
            reg_date=datetime.datetime.now()
        )
        g.current_user.projects.append(project)
        g.db_session.commit()
        return jsonify({'success': True})
