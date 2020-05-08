from wtforms import PasswordField, StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.fields.html5 import EmailField, DateTimeLocalField
from wtforms.widgets.html5 import ColorInput
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()],
                       render_kw={"class": "input-str form-control", "type": "email",
                                  "required": True})
    username = StringField('Имя пользователя', validators=[DataRequired()],
                           render_kw={"class": "input-str form-control", "required": True})

    first_name = StringField('Имя', validators=[DataRequired()],
                             render_kw={"class": "input-str form-control", "type": "name",
                                        "required": True})
    last_name = StringField('Фамилия', validators=[DataRequired()],
                            render_kw={"class": "input-str form-control", "type": "surname",
                                       "required": True})

    password = PasswordField('Пароль', validators=[DataRequired()],
                             render_kw={"class": "input-str form-control", "type": "password",
                                        "required": True})
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()],
                                   render_kw={"class": "input-str form-control", "type": "password",
                                              "required": True})

    submit = SubmitField('Начать')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        default = "input-str form-control"
        self.email.render_kw["class"] = default
        self.username.render_kw["class"] = default
        self.first_name.render_kw["class"] = default
        self.last_name.render_kw["class"] = default
        self.password.render_kw["class"] = default
        self.password_again.render_kw["class"] = default


class LoginForm(FlaskForm):
    label = 'Email или имя пользователя'
    email = StringField(label, validators=[DataRequired()], render_kw={
        "class": "input-str form-control",
        "required": True,
        "placeholder": label
    })

    label = 'Пароль'
    password = PasswordField(label, validators=[DataRequired()], render_kw={
        "class": "input-str form-control",
        "type": "password",
        "required": True,
        "placeholder": label
    })

    submit = SubmitField('Войти')


class ProjectForm(FlaskForm):
    project_name = StringField('Название проекта', validators=[DataRequired()],
                               render_kw={"class": "input-str form-control", "required": True})
    title = StringField('Заголовок', validators=[DataRequired()],
                        render_kw={"class": "input-str form-control", "required": True})
    description = StringField('Описание', render_kw={"class": "input-str form-control"})

    submit = SubmitField('Создать')

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        default = "input-str form-control"
        self.project_name.render_kw["class"] = default


class TaskForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()],
                        render_kw={"class": "input-str", "required": True})
    description = StringField('Описание', render_kw={"class": "input-str"})
    deadline = DateTimeLocalField('Дата дедлайна', format='%Y-%m-%dT%H:%M', validators=[DataRequired()],
                                  render_kw={"class": "input-str", "required": True})
    worker = SelectField('Ответственный за работу', choices=[('1', 'aba'), ('2', 'abacaba'), ('3', 'abacabadabacaba')],
                         render_kw={"class": "input-str"})
    tag = StringField('Тег', render_kw={"class": "input-str"})
    color_field = StringField('Цвет', render_kw={"class": "input-str"}, default="#ffffff")
    color_input = ColorInput()

    submit = SubmitField("Отправить")

    def __init__(self, users, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.worker.choices = [(str(user["id"]), f"{user['first_name']} {user['last_name']}")
                               for user in users]


class AddUserForm(FlaskForm):
    users = SelectMultipleField('Выберите пользователей для добавления', render_kw={"class": "select-users"})
    submit = SubmitField('Добавить')

    def __init__(self, users, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.users.choices = [(str(user["id"]), f"{user['first_name']} {user['last_name']}")
                              for user in users]
