import requests
from flask import send_from_directory, render_template, url_for
from werkzeug.utils import redirect
from misschedule import app
from misschedule.forms import RegisterForm
from pickle import dumps


@app.route("/")
def index():
    return send_from_directory('static/html', 'index.html')


@app.route('/signup', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        requests.post('http://127.0.0.1:5000/api/users',
                      dumps({
                          'username': form.username.data,
                          'email': form.email.data,
                          'first_name': form.first_name.data,
                          'last_name': form.last_name.data,
                          'password': form.password.data
                      }))
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           style_file=url_for('static', filename='css/register.css'))
