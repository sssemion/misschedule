import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from api.data.chat import Chat
from api.data.db_session import SqlAlchemyBase
from api.data.task import Task

association_table = sqlalchemy.Table('user_to_project', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('user', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')),
                                     sqlalchemy.Column('project', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('projects.id')),
                                     sqlalchemy.Column('position', sqlalchemy.String)
                                     )


class Project(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_leader_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    project_name = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    team_leader = orm.relation('User', foreign_keys=[team_leader_id])

    users = orm.relation("User",
                         secondary="user_to_project",
                         back_populates="projects",
                         lazy="subquery")

    tasks = orm.relation("Task", back_populates="project", foreign_keys=[Task.project_id],
                         lazy="subquery", cascade="all, delete, delete-orphan")
    chats = orm.relation("Chat", back_populates="project", foreign_keys=[Chat.project_id],
                         lazy="subquery", cascade="all, delete, delete-orphan")

    def __eq__(self, other):
        return self.id == other.id
