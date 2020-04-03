from flask import jsonify
from flask_restful import abort, Resource

from api.data import db_session
from api.resources.parsers import user_parser
from api.data.user import User


def abort_if_user_not_found(func):
    def new_func(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        return func(self, user_id)

    return new_func


class UserResource(Resource):
    @abort_if_user_not_found
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('email', 'first_name', 'last_name', 'reg_date'))})

    @abort_if_user_not_found
    def delete(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):

    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('email', 'first_name', 'last_name', 'reg_date')) for item in user]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = User(
            email=args['email'],
            first_name=args['first_name'],
            last_name=args['last_name'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
