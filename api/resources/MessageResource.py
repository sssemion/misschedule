import datetime

from flask import jsonify, g
from flask_restful import abort, Resource

from api.auth import token_auth
from api.data import db_session
from api.data.chat import Chat
from api.data.message import Message
from api.resources.parsers import message_parser_for_updating, message_parser_for_adding


def abort_if_message_not_found(func):
    def new_func(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        if not message:
            abort(404, success=False, message=f"Message {message_id} not found")
        return func(self, message_id)

    return new_func


class MessageResource(Resource):
    @abort_if_message_not_found
    @token_auth.login_required
    def get(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        if g.current_user not in message.chat.users:
            abort(403, success=False)
        return jsonify({'message': message.to_dict_myself()})

    @abort_if_message_not_found
    @token_auth.login_required
    def delete(self, message_id):
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        if g.current_user != message.chat.user:
            abort(403, success=False)
        session.delete(message)
        session.commit()
        return jsonify({'success': True})

    @abort_if_message_not_found
    @token_auth.login_required
    def put(self, message_id):
        args = message_parser_for_updating.parse_args(strict=True)  # Вызовет ошибку, если запрос
        # будет содержать поля, которых нет в парсере
        session = db_session.create_session()
        message = session.query(Message).get(message_id)
        # Если пользователь пытается редактировать не свое сообщение
        if g.current_user != message.chat.user:
            abort(403, success=False)
        for key, value in args.items():
            if value is not None:
                exec(f"message.{key} = '{value}'")
        session.commit()
        return jsonify({'success': True})


class MessageListResource(Resource):
    @token_auth.login_required
    def get(self):
        session = db_session.create_session()
        messages = session.query(Message).filter(Message.user_id == g.current_user.id)
        return jsonify({
            'messages': [
                {'message': message.to_dict_myself()}
                for message in messages],
        })

    @token_auth.login_required
    def post(self):
        args = message_parser_for_adding.parse_args(strict=True)
        session = db_session.create_session()
        chat = session.query(Chat).get(args['chat_id'])
        # Если чат не найден
        if chat is None:
            abort(404, success=False, message=f"Chat {args['chat_id']} not found")
        # Если текущий пользователь не состоит в чате
        if chat not in g.current_user.chats:
            abort(403, success=False)
        # Если пытаются отправить пустое сообщение
        if not args["message"]:
            abort(400, success=False, message="Message can not be empty")
        message = Message(
            chat_id=args['chat_id'],
            user_id=g.current_user.id,
            message=args['message'],
            date=datetime.datetime.now()
        )
        session.add(message)
        session.commit()
        return jsonify({'success': True,
                        'user': message.user.to_dict_myself(),
                        'date': ":".join(str(message.date).split(":")[:-1])
                        })
