from flask import jsonify
from flask_restful import Resource, abort

from api.data import db_session
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
    def get(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        return jsonify({'task': task.to_dict()})

    @abort_if_task_not_found
    def delete(self, task_id):
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        session.delete(task)
        session.commit()
        return jsonify({'success': True})

    @abort_if_task_not_found
    def put(self, task_id):
        args = task_parser_for_updating.parse_args()
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        for key, value in args.items():
            exec(f"task.{key} = value")
        session.commit()
        return jsonify({'success': True})


class TaskListResource(Resource):
    def post(self):
        args = task_parser_for_adding.parse_args()
        session = db_session.create_session()
        task = Task(
            project_id=args['project_id'],
            title=args['title'],
            description=args['description'],
            date=args['date'],
            deadline=args['deadline'],
            creator_id=args['creator_id'],
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
