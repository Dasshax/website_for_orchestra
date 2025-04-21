from flask import Flask, render_template, redirect
from data import db_session
import json
from data.users import Users, CONVERT_TO_RUSSIAN
import datetime
from data.images import Images
from data.videos import Videos
from data.audio import Audios
from data.classes import RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
db_session.global_init("db/users.db")

app.config['SECRET_KEY'] = 'FROLOV_NIKITA_LOX'

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
            image = session.query(Images).filter(Images.id == event['image']).first()
            event['image'] = f"static/images/{image.file_name}"
        return render_template('./index.html',
                               afisha=afisha_data,
                               news=NA, not_registered=1)
        a = 1 / 0
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/support')
def support():
    try:
        return render_template('support.html', not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/about')
def about():
    try:
        return render_template('about.html', not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/contacts')
def contacts():
    try:
        return render_template('contacts.html', not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/archive')
def archive():
    try:
        conc = open('data/concerts.json', encoding='utf-8')
        f = conc.read()
        concerts = json.loads(f)
        session = db_session.create_session()
        for event in concerts:
            video = session.query(Videos).filter(Videos.id == event['video_file']).first()
            try:
                event['video_file'] = f"static/videos/{video.file_name}"
            except Exception as err:
                print(err)
            audio = session.query(Audios).filter(Audios.id == event['audio_file']).first()
            try:
                event['audio_file'] = f"static/audio/{audio.file_name}"
            except Exception as err:
                print(err)
        return render_template('archive.html', concerts=concerts, not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/actual_events')
def actual_events():
    try:
        return render_template('actual_events.html', not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)




@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    try:
        profile_id = int(profile_id)
        session = db_session.create_session()
        user = session.query(Users).filter(Users.id == profile_id).first()
        data = []
        if user:
            for key in CONVERT_TO_RUSSIAN.keys():
                exec(f'data.append(((CONVERT_TO_RUSSIAN[key] + ":"), user.{key}))')
            images = session.query(Images).filter(Images.author_id == profile_id).all()
            data1 = []
            for i in images:
                data1.append((i.file_name, i.id, i.date))

            videos = session.query(Videos).filter(Videos.author_id == profile_id).all()
            data2 = []
            for i in videos:
                data2.append((i.file_name, i.id, i.date))

            audio = session.query(Audios).filter(Audios.author_id == profile_id).all()
            data3 = []

            for i in audio:
                data3.append((i.file_name, i.id, i.date))
            if user.profile_image:
                print()
                image_profile = user.profile_image
            else:
                image_profile = "billy.jpg"
            return render_template('profile.html', name=user.username, not_registered=0,
                                   user_information=data, profile_image=image_profile, image_information=data1,
                                   video_information=data2, audio_information=data3)
        else:
            return render_template('nt_exist.html', id=profile_id, type="Пользователя",
                                   not_registered=0)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=0)

@app.route('/test')
def test():
    session = db_session.create_session()
    return "test"

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    errors = []
    if form.validate_on_submit():
        session = db_session.create_session()
        new_user_name = form.username.data
        users = session.query(Users).filter(Users.username == new_user_name).first()
        if users:
            errors.append("Пользователь с таким именем уже существует.")
        else:
            new_user_email = form.email.data
            users = session.query(Users).filter(Users.email == new_user_email).first()
            if users:
                errors.append("Пользователь с такой почтой уже существует.")
            else:
                new_user = Users()
                new_user.username = new_user_name
                new_user.email = new_user_email
                new_user.password_hash = generate_password_hash(form.password.data)
                new_user.first_name = form.first_name.data
                new_user.last_name = form.last_name.data
                new_user.bio = form.bio.data

                last_user =  session.query(Users).order_by(Users.id.desc()).first()
                new_user.id = last_user.id + 1

                session.add(new_user)
                session.commit()
                return redirect("/")
    return render_template('registration.html', form=form, additional_errors=errors)


@app.route('/enter')
def enter():
    return "enter"

@app.route('/my_profile')
def my_profile():
    return redirect("profile/1")


if __name__ == '__main__':
    app.run(port=8080,  host='127.0.0.1')