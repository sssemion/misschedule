import sqlalchemy
import datetime

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
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    first_name = sqlalchemy.Column(sqlalchemy.String)
    last_name = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    projects = orm.relation("Project",
                            secondary="user_to_project",
                            backref="user")

    created_tasks = orm.relation("Task", back_populates="creator", foreign_keys=[Task.creator_id], lazy="subquery")
    performing_tasks = orm.relation("Task", back_populates="worker", foreign_keys=[Task.worker_id], lazy="subquery")


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
