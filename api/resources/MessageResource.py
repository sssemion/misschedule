from flask import jsonify
from flask_restful import abort, Resource

from api.data import db_session
from api.data.message import Message
from api.resources.parsers import message_parser_for_updating, message_parser_for_adding


def abort_if_message_not_found(func):
    def new_func(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        if not message:
            abort(404, message=f"Message {message_id} not found")
        return func(self, message_id)

    return new_func


class MessageResource(Resource):
    @abort_if_message_not_found
    def get(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        return jsonify({'message': message.to_dict(only=('chat_id', 'user_id', 'message'))})

    @abort_if_message_not_found
    def delete(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        session.delete(message)
        session.commit()
        return jsonify({'success': True})

    @abort_if_message_not_found
    def put(self, message_id):
        args = message_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        for key, value in args.items():
            if value is not None:
                exec(f"message.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class MessageListResource(Resource):
    def get(self):
        session = db_session.create_session()
        messages = session.query(Message).all()
        return jsonify({
            'messages': [
                {'message': message.to_dict(only=('chat_id', 'user_id', 'message'))}
                for message in messages],
        })

    def post(self):
        args = message_parser_for_adding.parse_args(strict=True)
        session = db_session.create_session()
        # noinspection PyArgumentList
        message = Message(
            chat_id=args['chat_id'],
            user_id=args['user_id'],
            message=args['message']
        )
        session.add(message)
        session.commit()
        return jsonify({'success': True})
