from wtforms import PasswordField, StringField, SubmitField, SelectMultipleField
from wtforms.fields.html5 import EmailField
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
        defualt = "input-str form-control"
        self.email.render_kw["class"] = defualt
        self.username.render_kw["class"] = defualt
        self.first_name.render_kw["class"] = defualt
        self.last_name.render_kw["class"] = defualt
        self.password.render_kw["class"] = defualt
        self.password_again.render_kw["class"] = defualt


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
    description = StringField('Описание', validators=[DataRequired()],
                              render_kw={"class": "input-str form-control", "required": True})

    submit = SubmitField('Создать')


class AddUserForm(FlaskForm):
    users = SelectMultipleField('Выберите пользователей для добавления', render_kw={"class": "select-users"})
    submit = SubmitField('Добавить')

    def __init__(self, users, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.users.choices = [(str(user["id"]), f"{user['first_name']} {user['last_name']}")
                              for user in users]
