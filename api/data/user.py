import base64
import datetime
import os

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from api.data.db_session import SqlAlchemyBase
from api.data.task import Task


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    first_name = sqlalchemy.Column(sqlalchemy.String)
    last_name = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    projects = orm.relation("Project",
                            secondary="user_to_project",
                            back_populates="users",
                            lazy="subquery")

    created_tasks = orm.relation("Task", back_populates="creator", foreign_keys=[Task.creator_id],
                                 lazy="subquery")
    performing_tasks = orm.relation("Task", back_populates="worker", foreign_keys=[Task.worker_id],
                                    lazy="subquery")

    chats = orm.relation("Chat",
                         secondary="user_to_chat",
                         back_populates="users",
                         lazy="subquery")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    token = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    token_expiration = sqlalchemy.Column(sqlalchemy.DateTime)

    def get_token(self, expires_in=3600):
        now = datetime.datetime.now()
        if self.token and self.token_expiration > now + datetime.timedelta(seconds=60):
            # Если токен действительный, возвращаем его
            return self.token
        # Иначе, генерируем новый и устанавливаем срок истечения через час
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + datetime.timedelta(seconds=expires_in)
        return self.token

    def revoke_token(self):
        # Отзыв токена (Время истечения изменяется на текущее - 1 секунда)
        self.token_expiration = datetime.datetime.now() - datetime.timedelta(seconds=1)

    def __eq__(self, other):
        return self.id == other.id
