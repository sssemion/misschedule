import requests
from flask import send_from_directory, render_template, url_for
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm


@app.route("/")
def index():
    return render_template('main-page.html')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password.render_kw["class"] = "input-str form-control is-invalid"
            form.password_again.render_kw["class"] = "input-str form-control is-invalid"
            return render_template('register.html', form=form, message="Пароли не совпадают")
        response = requests.post('http://127.0.0.1:5000/api/users', {
            'username': form.username.data,
            'email': form.email.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'password': form.password.data
        })

        data = response.json()

        if data['success']:
            return redirect('/login')
        if response.status_code == 400:
            if f"User {form.username.data} " in data.get('message', ''):
                form.username.render_kw["class"] = "input-str form-control is-invalid"
                form.username.errors.append('Имя уже занято')
            if f"email {form.email.data} " in data.get('message', ''):
                form.email.render_kw["class"] = "input-str form-control is-invalid"
                form.email.errors.append('Email уже занят')
        # TODO: проверка надежности пароля
    return render_template('register.html', form=form)
