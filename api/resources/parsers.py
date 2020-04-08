import datetime

from flask_restful import reqparse

user_parser_for_adding = reqparse.RequestParser()
user_parser_for_adding.add_argument('email', required=True)
user_parser_for_adding.add_argument('username', required=True)
user_parser_for_adding.add_argument('first_name', required=True)
user_parser_for_adding.add_argument('last_name', required=True)
user_parser_for_adding.add_argument('password', required=True)

user_parser_for_updating = reqparse.RequestParser()
user_parser_for_updating.add_argument('username')
user_parser_for_updating.add_argument('first_name')
user_parser_for_updating.add_argument('last_name')
user_parser_for_updating.add_argument('password')

project_parser_for_adding = reqparse.RequestParser()
project_parser_for_adding.add_argument('project_name', required=True)
project_parser_for_adding.add_argument('title', required=True)
project_parser_for_adding.add_argument('description', required=True)

project_parser_for_updating = reqparse.RequestParser()
project_parser_for_updating.add_argument('title')
project_parser_for_updating.add_argument('project_name')
project_parser_for_updating.add_argument('description')

task_parser_for_adding = reqparse.RequestParser()
task_parser_for_adding.add_argument('project_id', required=True, type=int)
task_parser_for_adding.add_argument('title', required=True)
task_parser_for_adding.add_argument('description')
task_parser_for_adding.add_argument('duration', type=int)
task_parser_for_adding.add_argument('creator_id', required=True, type=int)
task_parser_for_adding.add_argument('worker_id', type=int)
task_parser_for_adding.add_argument('tag')
task_parser_for_adding.add_argument('color')
task_parser_for_adding.add_argument('condition', type=int, choices=[0, 1, 2], default=0)
task_parser_for_adding.add_argument('items', type=dict)
task_parser_for_adding.add_argument('image', type=str)

task_parser_for_updating = reqparse.RequestParser()
task_parser_for_updating.add_argument('title')
task_parser_for_updating.add_argument('description')
task_parser_for_updating.add_argument('duration')
task_parser_for_updating.add_argument('worker_id', type=int)
task_parser_for_updating.add_argument('tag')
task_parser_for_updating.add_argument('color')
task_parser_for_updating.add_argument('condition', type=int, choices=[0, 1, 2])
task_parser_for_updating.add_argument('items', type=dict)
task_parser_for_updating.add_argument('image', type=str)

chat_parser_for_adding = reqparse.RequestParser()
chat_parser_for_adding.add_argument('project_id', required=True)
chat_parser_for_adding.add_argument('title', required=True)

chat_parser_for_updating = reqparse.RequestParser()
chat_parser_for_updating.add_argument('title')

message_parser_for_adding = reqparse.RequestParser()
message_parser_for_adding.add_argument('chat_id', required=True, type=int)
message_parser_for_adding.add_argument('user_id', required=True, type=int)
message_parser_for_adding.add_argument('message', required=True, type=str)

message_parser_for_updating = reqparse.RequestParser()
message_parser_for_updating.add_argument('message')
