import datetime

from flask import jsonify
from flask_restful import Resource, abort

from api.data import db_session
from api.data.task import Task


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
        session = db_session.create_session()
        task = session.query(Task).get(task_id)
        # TODO: возможнлсть изменить некоторые поля задачи


class TaskListResource(Resource):
    from flask_restful import reqparse

    parser = reqparse.RequestParser()
    parser.add_argument('project_id', required=True, type=int)
    parser.add_argument('title', required=True)
    parser.add_argument('description')
    parser.add_argument('date', type=datetime.datetime)
    parser.add_argument('deadline')
    parser.add_argument('creator_id', required=True, type=int)
    parser.add_argument('worker_id', type=int)
    parser.add_argument('tag')
    parser.add_argument('color')
    parser.add_argument('condition', type=int, choices=[0, 1, 2])
    parser.add_argument('items', type=dict)
    parser.add_argument('image', type=str)

    def post(self):
        args = self.parser.parse_args()
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
