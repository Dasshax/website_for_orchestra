from flask import Flask, render_template, redirect
from werkzeug.utils import secure_filename
import os
from data import db_session
import json
from data.users import Users, CONVERT_TO_RUSSIAN
import datetime
from data.images import Images
from data.videos import Videos
from data.audio import Audios
from data.classes import RegistrationForm, LoginForm, UploadFormImage, UploadFormAudio, UploadFormVideo
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__)
db_session.global_init("db/users.db")
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'FROLOV_NIKITA_LOX'


def get_registred_id():
    if current_user.is_authenticated:
        return current_user.id
    else:
        print(1)
        return 0


def get_registred_image():
    if current_user.is_authenticated:
        if current_user.profile_image:
            return current_user.profile_image
        else:
            return "billy.jpg"
    else:
        return "billy.jpg"

def get_is_admin():
    if current_user.is_authenticated:
        return current_user.is_admin
    else:
        return False

@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(Users).get(user_id)


@app.route('/')
@app.route('/index')
def index():
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
                           news=NA, not_registered=get_registred_id(), profile_image=get_registred_image(),
                           is_admin=get_is_admin())


@app.route('/support')
def support():
    try:
        return render_template('support.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/about')
def about():
    try:
        return render_template('about.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/contacts')
def contacts():
    try:
        return render_template('contacts.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


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
        return render_template('archive.html', concerts=concerts, not_registered=get_registred_id(),
                               profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/actual_events')
def actual_events():
    try:
        return render_template('actual_events.html', not_registered=get_registred_id(),
                               profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/profile/<int:profile_id>')
def profile(profile_id):
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
            if i.operation_type == "EXIST":
                data1.append((i.file_name, i.id, i.date, i.operation_type))
        videos = session.query(Videos).filter(Videos.author_id == profile_id).all()
        data2 = []
        for i in videos:
            data2.append((i.file_name, i.id, i.date))

        audio = session.query(Audios).filter(Audios.author_id == profile_id).all()
        data3 = []

        for i in audio:
            data3.append((i.file_name, i.id, i.date))
        if user.profile_image:
            image_profile = user.profile_image
        else:
            image_profile = "billy.jpg"
        this_user = False
        if current_user.is_authenticated:
            if current_user.id == user.id:
                this_user = True
        return render_template('profile.html', name=user.username, not_registered=get_registred_id(),
                               user_information=data, profile_image=image_profile, image_information=data1,
                               video_information=data2, audio_information=data3, this_user=this_user, user_id=profile_id,
                               is_curr_user_admin=get_is_admin())
    else:
        return render_template('nt_exist.html', id=profile_id, type="Пользователя",
                               not_registered=get_registred_id(), profile_image=get_registred_image())


@app.route('/test')
def test():
    session = db_session.create_session()
    return "test"


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    try:
        if current_user.is_authenticated:
            return redirect("/")
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
                    last_user = session.query(Users).order_by(Users.id.desc()).first()
                    new_user.id = last_user.id + 1
                    data = str(datetime.date.today())
                    time = str(datetime.datetime.now().strftime("%H:%M:%S"))
                    new_user.registration_date = (data + " " + time)
                    session.add(new_user)
                    session.commit()
                    return redirect("/")
        return render_template('registration.html', form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect("/")
        form = LoginForm()
        errors = []
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(Users).filter(Users.username == form.username.data).first()
            if user:
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    return redirect("/")
                else:
                    errors.append("Неверный пароль.")
            else:
                errors.append("Пользователя с таким именем не существует.")
        return render_template("login.html", form=form, additional_errors=errors, not_registered=get_registred_id(),
                               profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/my_profile')
@login_required
def my_profile():
    cur_id = current_user.id
    return redirect(f"profile/{cur_id}")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/delete_from_<string:redirto>/<string:typ>/<int:del_id>')
@login_required
def delete_from(redirto, typ, del_id):
    session = db_session.create_session()
    redirto = str(redirto)
    if typ == "image":
        image = session.query(Images).filter(Images.id == del_id).first()
        if image:
            if (image.author_id == current_user.id) or get_is_admin():
                image.operation_type = "DELETED"
                try:
                    os.remove('static/images/' + image.file_name)
                except Exception as err:
                    print(err)
    if typ == "video":
        video = session.query(Videos).filter(Videos.id == del_id).first()
        if video:
            if (video.author_id == current_user.id) or get_is_admin():
                video.operation_type = "DELETED"
                try:
                    os.remove('static/videos/' + video.file_name)
                except Exception as err:
                    print(err)
    if typ == "audio":
        audio = session.query(Audios).filter(Audios.id == del_id).first()
        if audio:
            if (audio.author_id == current_user.id) or get_is_admin():
                audio.operation_type = "DELETED"
                try:
                    os.remove('static/audio/' + video.file_name)
                except Exception as err:
                    print(err)

    session.commit()

    if "profile" in redirto:
        past = redirto[redirto.find("_") + 1:]

        return redirect(f"/profile/{past}")


@app.route('/load/image/<type>', methods=['GET', 'POST'])
@login_required
def load_image(type):
    try:
        form = UploadFormImage()
        errors = []
        session = db_session.create_session()
        form_title = ""
        if type == "prf":
            form_title = "профиля"
        if type == "adm":
            if get_is_admin():
                form_title = "использования в материалах сайта"
            else:
                return redirect("/")
        if form.validate_on_submit():
            images = session.query(Images).filter(Images.file_name == form.file.data.filename,
                                                  Images.operation_type == "Exist").first()
            if not images:
                form.file.data.save('static/images/' + form.file.data.filename)
                user = session.query(Users).filter(Users.id == current_user.id).first()
                if user:
                    if type == "prf":
                        if user.profile_image and not get_is_admin():
                            image = session.query(Images).filter(Images.file_name == user.profile_image).first()
                            if image:
                                image.operation_type = "DELETED"
                                try:
                                    os.remove('static/images/' + user.profile_image)
                                except Exception as err:
                                    print(err)
                    last_image = session.query(Images).order_by(Images.id.desc()).first()
                    image = Images()
                    image.id = last_image.id + 1
                    image.file_name = form.file.data.filename
                    image.operation_type = "EXIST"
                    image.date = (str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%H:%M:%S")))
                    image.author_id = user.id
                    session.merge(image)
                    if type == "prf":
                        user.profile_image = form.file.data.filename
                    session.commit()
                    return redirect("/my_profile")
            else:
                errors.append("Изображение с таким именем уже существует.")

        return render_template("load_image.html", form=form, additional_errors=errors, not_registered=get_registred_id(),
                               profile_image=get_registred_image(), title=form_title)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())

@app.route('/load/video', methods=['GET', 'POST'])
@login_required
def load_video():
    try:
        form = UploadFormVideo()
        errors = []
        session = db_session.create_session()
        if not get_is_admin():
            return redirect("/")
        if form.validate_on_submit():
            videos = session.query(Videos).filter(Videos.file_name == form.file.data.filename,
                                                  Images.operation_type == "Exist").first()
            if not videos:
                form.file.data.save('static/videos/' + form.file.data.filename)
                user = session.query(Users).filter(Users.id == current_user.id).first()
                if user:
                    last_video = session.query(Videos).order_by(Videos.id.desc()).first()
                    video = Videos()
                    video.id = last_video.id + 1
                    video.file_name = form.file.data.filename
                    video.operation_type = "EXIST"
                    video.date = (str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%H:%M:%S")))
                    video.author_id = user.id
                    session.merge(video)
                    session.commit()
                    return redirect("/my_profile")
            else:
                errors.append("Видео с таким именем уже существует.")

        return render_template("load_video_audio.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image(),
                               title='видео')
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/load/audio', methods=['GET', 'POST'])
@login_required
def load_audio():
    try:
        form = UploadFormAudio()
        errors = []
        session = db_session.create_session()
        if not get_is_admin():
            return redirect("/")
        if form.validate_on_submit():
            audios = session.query(Audios).filter(Audios.file_name == form.file.data.filename,
                                                  Images.operation_type == "Exist").first()
            if not audios:
                form.file.data.save('static/audio/' + form.file.data.filename)
                user = session.query(Users).filter(Users.id == current_user.id).first()
                if user:
                    last_audio = session.query(Audios).order_by(Audios.id.desc()).first()
                    audio = Audios()
                    audio.id = last_audio.id + 1
                    audio.file_name = form.file.data.filename
                    audio.operation_type = "EXIST"
                    audio.date = (str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%H:%M:%S")))
                    audio.author_id = user.id
                    session.merge(audio)
                    session.commit()
                    return redirect("/my_profile")
            else:
                errors.append("Аудио с таким именем уже существует.")

        return render_template("load_video_audio.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image(),
                               title="аудио")
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())

@app.route("/move_to_archive_<typ>/<int:id>")
@login_required
def move_to_archive(typ, id):
    if typ == "event":
        events = open('data/actual_events.json', encoding='utf-8')
        f = events.read()
        afisha_data = json.loads(f)
        for k in afisha_data:
            if id == k['id']:
                k['is_in_archive'] = True
        events.close()
        events = open('data/actual_events.json', 'w', encoding='utf-8')
        json.dump(afisha_data, events, ensure_ascii=False)
    if typ == "article":
        na = open('data/news_articles.json', encoding='utf-8')
        f1 = na.read()
        NA = json.loads(f1)
        for k in NA:
            if id == k['id']:
                k['is_in_archive'] = True
        na.close()
        na = open('data/news_articles.json', 'w', encoding='utf-8')
        json.dump(NA, na, ensure_ascii=False)
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
