from flask import jsonify
from flask_restful import abort, Resource

from api.data import db_session
from api.data.chat import Chat
from api.resources.parsers import chat_parser_for_updating, chat_parser_for_adding


def abort_if_chat_not_found(func):
    def new_func(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        if not chat:
            abort(404, message=f"Chat {chat_id} not found")
        return func(self, chat_id)

    return new_func


class ChatResource(Resource):
    @abort_if_chat_not_found
    def get(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        return jsonify({
            'chat': chat.to_dict(only=('title', 'project_id')),
            'users': [item.id for item in chat.users]})

    @abort_if_chat_not_found
    def delete(self, chat_id):
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        session.delete(chat)
        session.commit()
        return jsonify({'success': True})

    @abort_if_chat_not_found
    def put(self, chat_id):
        args = chat_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        chat = session.query(Chat).get(chat_id)
        for key, value in args.items():
            if value is not None:
                exec(f"chat.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class ChatListResource(Resource):
    def get(self):
        session = db_session.create_session()
        chats = session.query(Chat).all()
        return jsonify({
            'chats': [
                {
                    'chat': chat.to_dict(only=('id', 'title', 'project_id')),
                    'users': [user.id for user in chat.users]
                }
                for chat in chats],
        })

    def post(self):
        args = chat_parser_for_adding.parse_args(strict=True)
        session = db_session.create_session()
        # noinspection PyArgumentList
        chat = Chat(
            project_id=args['project_id'],
            title=args['title']
        )
        session.add(chat)
        session.commit()
        return jsonify({'success': True})
