import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase

user_to_chat = sqlalchemy.Table('user_to_chat', SqlAlchemyBase.metadata,
                                sqlalchemy.Column('user', sqlalchemy.Integer,
                                                  sqlalchemy.ForeignKey('users.id')),
                                sqlalchemy.Column('chat', sqlalchemy.Integer,
                                                  sqlalchemy.ForeignKey('chats.id'))
                                )


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    project_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("projects.id"), nullable=False)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    users = orm.relation("User", secondary="user_to_chat", backref="chat")
    messages = orm.relation("Message", back_populates="chat", cascade="all, delete, delete-orphan")
    project = orm.relation("Project", foreign_keys=[project_id])
