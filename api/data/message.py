import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"), nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    message = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user = orm.relation("User", foreign_keys=[user_id])
    chat = orm.relation("Chat", foreign_keys=[chat_id])

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id
