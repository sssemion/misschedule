import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase


class TaskItem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'task_items'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"), nullable=False)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    completed_by_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"),
                                        default=None)
    completion_date = sqlalchemy.Column(sqlalchemy.DateTime, default=None)
    description = sqlalchemy.Column(sqlalchemy.String)

    task = orm.relation("Task", foreign_keys=[task_id])
    completed_by = orm.relation("User", foreign_keys=[completed_by_id])

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def to_dict_myself(self):
        return self.to_dict(only=("id", "title", "description", "completed", "completed_by_id", "completion_date"))
