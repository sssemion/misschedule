from flask import jsonify, g
from flask_restful import Resource, abort

from api.auth import token_auth
from api.data import db_session
from api.data.project import Project
from api.data.task import Task
from api.resources.parsers import task_parser_for_adding, task_parser_for_updating


def abort_if_task_not_found(func):
    def new_func(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if not task:
            abort(404, message=f"User {task_id} not found")
        return func(self, task_id)

    return new_func


class TaskResource(Resource):
    @abort_if_task_not_found
    @token_auth.login_required
    def get(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user not in task.project.users:
            abort(403)
        return jsonify({'task': task.to_dict()})

    @abort_if_task_not_found
    @token_auth.login_required
    def delete(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user != task.creator:
            abort(403)
        session.delete(task)
        session.commit()
        return jsonify({'success': True})

    @abort_if_task_not_found
    @token_auth.login_required
    def put(self, task_id):  # Метод для полного изменения (доступно только для создателя)
        # TODO: Метод для изменения состояния и пунктов (доступно для исполнителя задачи)
        args = task_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user != task.creator:
            abort(403)
        if 'title' in args and args['title'] in map(lambda x: x.title, task.project.tasks):
            abort(400, message=f"Task with title '{args['title']}' already exists")
        for key, value in args.items():
            if value is not None:
                exec(f"task.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class TaskListResource(Resource):
    @token_auth.login_required
    def post(self):
        args = task_parser_for_adding.parse_args()
        session = db_session.create_session()
        project = session.query(Project).get(args['project_id'])
        if project is None:
            abort(404, message=f"Project {args['project_id']} not found")
        if project not in g.current_user.projects:
            abort(403)
        if args['title'] in map(lambda x: x.title, project.tasks):
            abort(400, message=f"Task with title '{args['title']}' already exists")
        task = Task(
            project_id=args['project_id'],
            title=args['title'],
            description=args['description'],
            duration=args['duration'],
            creator_id=g.current_user.id,
            worker_id=args['worker_id'],
            tag=args['tag'],
            color=args['color'],
            condition=args['condition'],
            items=args['items'],
            image=args['image'],
        )
        session.add(task)
        session.commit()
        return jsonify({'success': True})
