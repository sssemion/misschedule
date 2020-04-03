import sqlalchemy
import datetime
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from api.data.db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('user to project', SqlAlchemyBase.metadata,
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
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    team_leader = orm.relation('User', foreign_keys=[team_leader_id])
