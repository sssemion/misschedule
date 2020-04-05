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

    users = orm.relation("User", secondary="user_to_chat", backref="chat")
