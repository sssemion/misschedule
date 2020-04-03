from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('email', required=True)
user_parser.add_argument('first_name', required=True)
user_parser.add_argument('last_name', required=True)
user_parser.add_argument('password', required=True)

project_parser = reqparse.RequestParser()
project_parser.add_argument('team_leader_id', required=True)
project_parser.add_argument('title', required=True)
project_parser.add_argument('description', required=True)
project_parser.add_argument('reg_date', required=True)
