import datetime

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from api import app
from api.data import db_session
from api.data.user import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    session = db_session.create_session()
    user = session.query(User).filter((User.username == username) | (User.email == username)).first()
    if user is None:
        return False
    if user.check_password(password):
        g.db_session = session
        g.current_user = user
        return True
    return False


@token_auth.verify_token
def verify_token(token):
    session = db_session.create_session()
    user = session.query(User).filter(User.token == token).first()
    if user is None or user.token_expiration < datetime.datetime.now():
        return False
    g.db_session = session
    g.current_user = user
    return True


@basic_auth.error_handler
def basic_auth_error():
    return jsonify({'success': False}), 401


@token_auth.error_handler
def token_auth_error():
    return jsonify({'success': False}), 401


@app.route('/api/login', methods=['POST'])
@basic_auth.login_required
# Путь получает в заголовках запроса логин и пароль пользователя (декоратор @basic.auth.login_required)
# и, если данные верны, возвращает токен. Чтобы защитить маршруты API с помощью токенов, необходимо
# добавить декоратор @token_auth.login_required
def get_token():
    token = g.current_user.get_token()
    g.db_session.commit()
    return jsonify({'success': True, 'token': {'token': token,
                                               'expires': str(g.current_user.token_expiration)}})


@app.route('/api/logout', methods=['POST'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    g.db_session.commit()
    g.current_user = None
    g.db_session = None
    return jsonify({'success': True})
