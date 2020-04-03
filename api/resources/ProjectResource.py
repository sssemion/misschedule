from flask import jsonify
from flask_restful import abort, Resource

from api.data import db_session
from api.resources.parsers import project_parser
from api.data.project import Project


def abort_if_project_not_found(func):
    def new_func(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        if not project:
            abort(404, message=f"project {project_id} not found")
        return func(self, project_id)

    return new_func


class ProjectResource(Resource):
    @abort_if_project_not_found
    def get(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        return jsonify({'project': project.to_dict(
            only=('team_leader_id', 'title', 'description', 'reg_date'))})

    @abort_if_project_not_found
    def delete(self, project_id):
        session = db_session.create_session()
        project = session.query(Project).get(project_id)
        session.delete(project)
        session.commit()
        return jsonify({'success': 'OK'})


class ProjectListResource(Resource):

    def get(self):
        session = db_session.create_session()
        project = session.query(Project).all()
        return jsonify({'project': [item.to_dict(
            only=('team_leader_id', 'title', 'description', 'reg_date')) for item in project]})

    def post(self):
        args = project_parser.parse_args()
        session = db_session.create_session()
        project = Project(
            team_leader_id=args['team_leader_id'],
            title=args['title'],
            description=args['description'],
            reg_date=args['reg_date']
        )
        session.add(project)
        session.commit()
        return jsonify({'success': 'OK'})
