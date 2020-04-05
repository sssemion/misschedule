from flask import Flask
from flask_restful import Api

from api.data import db_session
from api.resources.ChatResource import ChatResource, ChatListResource
from api.resources.MessageResource import MessageResource, MessageListResource
from api.resources.ProjectResource import ProjectResource, ProjectListResource
from api.resources.UserResource import UserResource, UserListResource
from api.resources.TaskResource import TaskResource, TaskListResource

app = Flask(__name__)
api = Api(app)

api.add_resource(UserResource, "/api/users/<int:user_id>")
api.add_resource(UserListResource, "/api/users")

api.add_resource(ProjectResource, "/api/projects/<int:project_id>")
api.add_resource(ProjectListResource, "/api/projects")

api.add_resource(TaskResource, "/api/tasks/<int:task_id>")
api.add_resource(TaskListResource, "/api/tasks")

api.add_resource(ChatResource, "/api/chats/<int:chat_id>")
api.add_resource(ChatListResource, "/api/chats")

api.add_resource(MessageResource, "/api/messages/<int:message_id>")
api.add_resource(MessageListResource, "/api/messages")

db_session.global_init("api/db/misschedule.sqlite")

from api import controllers
