import datetime

from flask import jsonify, g
from flask_restful import abort, Resource

from api.auth import token_auth
from api.data import db_session
from api.resources.parsers import user_parser_for_adding, user_parser_for_updating
from api.data.user import User


def abort_if_user_not_found(func):
    def new_func(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if not user:
            abort(404, success=False, message=f"User {user_id} not found")
        return func(self, user_id)

    return new_func


def only_for_current_user(func):
    def new_func(self, user_id):
        if user_id != g.current_user.id:
            abort(403, success=False)
        return func(self, user_id)

    return new_func


class UserResource(Resource):
    @abort_if_user_not_found
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict_myself()})

    @abort_if_user_not_found
    @token_auth.login_required
    @only_for_current_user
    def delete(self, user_id):
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': True})

    @abort_if_user_not_found
    @token_auth.login_required
    @only_for_current_user
    def put(self, user_id):
        args = user_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос 
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if 'username' in args and session.query(User).filter(User.username == args['username']).first() is not None:
            abort(400, success=False, message=f"User {args['username']} already exists")
        for key, value in args.items():
            if value is not None:
                exec(f"user.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class UserListResource(Resource):

    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict_myself() for item in user]})

    def post(self):
        args = user_parser_for_adding.parse_args(strict=True)
        session = db_session.create_session()
        if session.query(User).filter(User.email == args['email']).first() is not None:
            abort(400, success=False, message=f"User with email {args['email']} already exists")
        if session.query(User).filter(User.username == args['username']).first() is not None:
            abort(400, success=False, message=f"User {args['username']} already exists")
        user = User(
            email=args['email'],
            username=args['username'],
            first_name=args['first_name'],
            last_name=args['last_name'],
            reg_date=datetime.datetime.now()
        )
        user.set_password(args['password'])
        token = user.get_token()
        session.add(user)
        session.commit()
        return jsonify({'success': True, 'authToken': {'token': token,
                                                       'expires': str(user.token_expiration)}})
