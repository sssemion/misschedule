import datetime

from flask_restful import reqparse

task_parser_for_adding = reqparse.RequestParser()
task_parser_for_adding.add_argument('project_id', required=True, type=int)
task_parser_for_adding.add_argument('title', required=True)
task_parser_for_adding.add_argument('description')
task_parser_for_adding.add_argument('date', type=datetime.datetime)
task_parser_for_adding.add_argument('deadline')
task_parser_for_adding.add_argument('creator_id', required=True, type=int)
task_parser_for_adding.add_argument('worker_id', type=int)
task_parser_for_adding.add_argument('tag')
task_parser_for_adding.add_argument('color')
task_parser_for_adding.add_argument('condition', type=int, choices=[0, 1, 2])
task_parser_for_adding.add_argument('items', type=dict)
task_parser_for_adding.add_argument('image', type=str)

task_parser_for_updating = reqparse.RequestParser()
task_parser_for_updating.add_argument('title')
task_parser_for_updating.add_argument('description')
task_parser_for_updating.add_argument('deadline')
task_parser_for_updating.add_argument('worker_id', type=int)
task_parser_for_updating.add_argument('tag')
task_parser_for_updating.add_argument('color')
task_parser_for_updating.add_argument('condition', type=int, choices=[0, 1, 2])
task_parser_for_updating.add_argument('items', type=dict)
task_parser_for_updating.add_argument('image', type=str)
