import datetime

from flask import jsonify, g
from flask_restful import abort, Resource

from api.auth import token_auth
from api.data import db_session
from api.data.chat import Chat
from api.data.project import Project
from api.resources.parsers import chat_parser_for_updating, chat_parser_for_adding


def abort_if_chat_not_found(func):
    def new_func(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        if not chat:
            abort(404, success=False, message=f"Chat {chat_id} not found")
        return func(self, chat_id)

    return new_func


def check_if_user_is_a_member(func):
    def new_func(self, chat_id):
        print(list(map(lambda x: x.id, g.current_user.chats)))
        if chat_id not in map(lambda x: x.id, g.current_user.chats):
            abort(403, success=False)
        return func(self, chat_id)

    return new_func


class ChatResource(Resource):
    @abort_if_chat_not_found
    @token_auth.login_required
    @check_if_user_is_a_member
    def get(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        return jsonify({
            'chat': chat.to_dict(only=('id','title', 'project_id')),
            'users': [item.to_dict(only=('id', 'username', 'email', 'first_name', 'last_name')) for item in chat.users]})

    @abort_if_chat_not_found
    @token_auth.login_required
    def delete(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        if chat.creator != g.current_user:
            abort(403, success=False)
        session.delete(chat)
        session.commit()
        return jsonify({'success': True})

    @abort_if_chat_not_found
    @token_auth.login_required
    def put(self, chat_id):
        args = chat_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        if 'title' in args and args['title'] in map(lambda x: x.title, g.current_user.chats):
            abort(400, success=False, message=f"Chat '{args['title']}' already exists")
        if chat.creator != g.current_user:
            abort(403, success=False)
        for key, value in args.items():
            if value is not None:
                exec(f"chat.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class ChatListResource(Resource):
    @token_auth.login_required
    def get(self):
        session = db_session.create_session()
        chats = session.query(Chat).all()
        return jsonify({
            'chats': [
                {
                    'chat': chat.to_dict(only=('id', 'title', 'project_id')),
                    'users': [user.to_dict(only=('id', 'username', 'email', 'first_name', 'last_name')) for user in chat.users]
                }
                for chat in g.current_user.chats],
        })

    @token_auth.login_required
    def post(self):
        args = chat_parser_for_adding.parse_args(strict=True)
        session = db_session.create_session()
        # noinspection PyArgumentList
        project = session.query(Project).get(args['project_id'])
        if project is None:
            abort(404, success=False, message=f"Project {args['project_id']} not found")
        if project not in g.current_user.projects:
            abort(403, success=False)
        if project.team_leader != g.current_user:
            abort(403, success=False)
        if 'title' in args and args['title'] in map(lambda x: x.title, g.current_user.chats):
            abort(400, success=False, message=f"Chat '{args['title']}' already exists")
        # noinspection PyArgumentList
        chat = Chat(
            project_id=args['project_id'],
            creator_id=g.current_user.id,
            title=args['title'],
            reg_date=datetime.datetime.now()
        )
        session.add(chat)
        session.commit()
        return jsonify({'success': True})
