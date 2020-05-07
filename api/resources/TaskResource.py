import datetime

from flask import jsonify, g
from flask_restful import Resource, abort

from api.auth import token_auth
from api.data import db_session
from api.data.project import Project
from api.data.task import Task
from api.data.task_item import TaskItem
from api.data.user import User
from api.resources.parsers import task_parser_for_adding, task_parser_for_updating


def abort_if_task_not_found(func):
    def new_func(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if not task:
            abort(404, success=False, message=f"Task {task_id} not found")
        return func(self, task_id)

    return new_func


class TaskResource(Resource):
    @abort_if_task_not_found
    @token_auth.login_required
    def get(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user not in task.project.users:
            abort(403, success=False)
        return jsonify({
            'task': task.to_dict(only=(
                "project_id", "title", "description", "duration", "worker_id", "creator_id", "tag",
                "color", "condition", "image", "date")),
            'items': [item.to_dict(
                only=("title", "description", "completed", "completed_by_id", "completion_date")) for
                item in task.items],
            'canYouEdit': g.current_user == task.worker or g.current_user == task.creator,
        })

    @abort_if_task_not_found
    @token_auth.login_required
    def delete(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user != task.creator:
            abort(403, success=False)
        session.delete(task)
        session.commit()
        return jsonify({'success': True})

    @abort_if_task_not_found
    @token_auth.login_required
    def put(self, task_id):  # Метод для полного изменения (доступно только для создателя)
        args = task_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        if g.current_user != task.creator:
            abort(403, success=False)
        if 'title' in args and args['title'] in map(lambda x: x.title, task.project.tasks):
            abort(400, success=False, message=f"Task with title '{args['title']}' already exists")
        for key, value in args.items():
            if value is not None:
                exec(f"task.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class TaskListResource(Resource):
    @token_auth.login_required
    def get(self):
        return jsonify({
            'tasks': [
                {
                    'task': task.to_dict(only=(
                        "project_id", "title", "description", "duration", "worker_id", "creator_id",
                        "tag", "color",
                        "condition", "image", "date")),
                    'items': [item.to_dict(only=(
                        "title", "description", "completed", "completed_by_id", "completion_date"))
                        for
                        item in task.items],
                    'canYouEdit': g.current_user == task.worker or g.current_user == task.creator,
                } for task in filter(lambda x: x.condition != 2, g.current_user.performing_tasks)
            ],
        })

    @token_auth.login_required
    def post(self):
        args = task_parser_for_adding.parse_args()
        session = db_session.create_session()
        project = session.query(Project).get(args['project_id'])
        if project is None:
            abort(404, success=False, message=f"Project {args['project_id']} not found")
        if project not in g.current_user.projects:
            abort(403, success=False)
        if args['title'] in map(lambda x: x.title, project.tasks):
            abort(400, success=False,
                  message=f"Task with title '{args['title']}' already exists")
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
            image=args['image'],
            date=datetime.datetime.now()
        )
        if args['items']:
            for title, description in args['items'].items():
                task.items.append(TaskItem(title=title, description=description))
        session.add(task)
        session.commit()
        return jsonify({'success': True})
