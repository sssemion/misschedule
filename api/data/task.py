import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    project_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("projects.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    duration = sqlalchemy.Column(sqlalchemy.Integer)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    tag = sqlalchemy.Column(sqlalchemy.String)
    color = sqlalchemy.Column(sqlalchemy.String, default="#ffffff")
    condition = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    image = sqlalchemy.Column(sqlalchemy.String)

    creator = orm.relation('User', foreign_keys=[creator_id])
    worker = orm.relation('User', foreign_keys=[worker_id])
    project = orm.relation('Project', foreign_keys=[project_id])

    items = orm.relation('TaskItem', back_populates='task', cascade="all, delete, delete-orphan")

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id
