from flask import Flask, render_template, redirect, url_for, session
from data import db_session
import json
from data.users import Users
from data.images import Images
from data.functions import *
from data.classes import *
from data.config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = params['SECRET_KEY']
db_session.global_init("db/users.db")
users = {}


@app.route('/')
@app.route('/index')
def index():
    try:
        events = open('data/actual_events.json', encoding='utf-8')
        f = events.read()
        afisha_data = json.loads(f)

        na = open('data/news_articles.json', encoding='utf-8')
        f1 = na.read()
        NA = json.loads(f1)

        session = db_session.create_session()
        for event in afisha_data:
            print(event)
            image = session.query(Images).filter(Images.id == event['image']).first()
            event['image'] = f"static/images/{image.file_name}"
        return render_template('./index.html',
                               afisha=afisha_data,
                               news=NA)
    except Exception as err:
        print(err)
        return render_template("error.html")


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/archive')
def archive():
    with open('data/concerts.json', encoding='utf-8') as conc:
        f = conc.read()
        concerts = json.loads(f)
    return render_template('archive.html', concerts=concerts)


@app.route('/actual_events')
def actual_events():
    return render_template('actual_events.html')


@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    profile_id = int(profile_id)
    session = db_session.create_session()
    user = session.query(Users).filter(Users.id == profile_id).first()
    if user:
        return render_template('profile.html', name=user.username)
    else:
        return render_template('nt_exist.html', id=profile_id, type="Пользователя")


@app.route('/test')
def test():
    session = db_session.create_session()
    return "test"


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Registration_Form()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        hashed_password = hash_password(password)

        if username in users:
            form.username.errors.append('Имя пользователя уже занято.')
            return render_template('register.html', form=form, title="Регистрация")

        users[username] = {'password_hash': hashed_password, 'email': email}
        print(f"Registered user: {username}")
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title="Регистрация")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login_Form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username not in users:
            form.username.errors.append('Неверное имя пользователя или пароль.')
            return render_template('login.html', form=form, title="Вход")

        user = users[username]
        if check_password(password, user['password_hash']):
            session['username'] = username
            print(f"Logged in user: {username}")
            return redirect(url_for('profile'))
        else:
            form.password.errors.append('Неверное имя пользователя или пароль.')
            return render_template('login.html', form=form, title="Вход")

    return render_template('login.html', form=form, title="Вход")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
