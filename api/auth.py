import datetime

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from api.data import db_session
from api.data.user import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


# Авторизация может происходить по логину и паролю и по токену. Евли авторизоваться по логину и паролю,
# то вернется токен
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


# Авторизация также может происходить по токену
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
