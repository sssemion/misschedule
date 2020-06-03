from flask import jsonify, g
from flask_restful import Resource, abort

from api.auth import token_auth
from api.data import db_session
from api.data.project import Project
from api.data.task import Task
from api.data.task_item import TaskItem
from api.resources.parsers import task_item_parser_for_adding, task_item_parser_for_updating


def abort_if_task_item_not_found(func):
    def new_func(self, task_item_id):
        session = db_session.create_session()
        task_item = session.query(TaskItem).get(task_item_id)
        if not task_item:
            abort(404, success=False, message=f"Task item {task_item_id} not found")
        return func(self, task_item_id)

    return new_func


class TaskItemResource(Resource):
    @abort_if_task_item_not_found
    @token_auth.login_required
    def get(self, task_item_id):
        session = db_session.create_session()
        task_item = session.query(TaskItem).get(task_item_id)
        if not (g.current_user == task_item.task.creator or g.current_user == task_item.task.worker):
            abort(403, success=False)
        return jsonify({'task_item': task_item.to_dict_myself()})

    @abort_if_task_item_not_found
    @token_auth.login_required
    def delete(self, task_item_id):
        session = db_session.create_session()
        task_item = session.query(TaskItem).get(task_item_id)
        if not (g.current_user == task_item.task.creator or g.current_user == task_item.task.worker):
            abort(403, success=False)
        session.delete(task_item)
        session.commit()
        return jsonify({'success': True})

    @abort_if_task_item_not_found
    @token_auth.login_required
    def put(self, task_item_id):
        args = task_item_parser_for_updating.parse_args(strict=True)
        session = db_session.create_session()
        task_item = session.query(TaskItem).get(task_item_id)
        if not (g.current_user == task_item.task.creator or g.current_user == task_item.task.worker):
            abort(403, success=False)
        if 'title' in args and args['title'] in map(lambda x: x.title, task_item.task.items):
            abort(400, success=False, message=f"Task item with title '{args['title']}' already exists")
        for key, value in args.items():
            if value is not None:
                exec(f"task_item.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class TaskItemListResource(Resource):
    @token_auth.login_required
    def post(self):
        args = task_item_parser_for_adding.parse_args()
        session = db_session.create_session()
        task = session.query(Task).get(args['task_id'])
        if task is None:
            abort(404, success=False, message=f"Task {args['task_id']} not found")
        if not (g.current_user == task.creator or g.current_user == task.worker):
            abort(403, success=False)
        if args['title'] in map(lambda x: x.title, task.items):
            abort(400, success=False, message=f"Task item with title '{args['title']}' already exists")
        if args['title'] == '':
            abort(400, success=False, message="Title cannot be empty")
        task_item = TaskItem(
            task_id=args['task_id'],
            title=args['title'],
            description=args['description'],
        )
        session.add(task_item)
        session.commit()
        return jsonify({'success': True, 'taskItem': {
            'id': task_item.id,
            'title': task_item.title,
            'description': task_item.description
        }})
