import sqlalchemy
import datetime
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    project_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("projects.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    duration = sqlalchemy.Column(sqlalchemy.Integer)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    tag = sqlalchemy.Column(sqlalchemy.String)
    color = sqlalchemy.Column(sqlalchemy.String, default="#ffffff")
    condition = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    items = sqlalchemy.Column(sqlalchemy.JSON)
    image = sqlalchemy.Column(sqlalchemy.String)

    creator = orm.relation('User', foreign_keys=[creator_id])
    worker = orm.relation('User', foreign_keys=[worker_id])
    project = orm.relation('Project', foreign_keys=[project_id])
