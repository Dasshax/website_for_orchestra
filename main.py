from flask import Flask, render_template, redirect
from werkzeug.utils import secure_filename
import os
from data.config import SECRET_KEY, SERVER, PORT, DB_NAME
from data import db_session
import json
from data.users import Users, CONVERT_TO_RUSSIAN
import datetime

from data.images import Images
from data.videos import Videos
from data.audio import Audios
from data.classes import (RegistrationForm, LoginForm, UploadFormImage, UploadFormAudio, UploadFormVideo, CreateEvent,
                          CreateNews, CreateConcert)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__)
db_session.global_init(DB_NAME)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = SECRET_KEY


def get_registred_id():
    """Получение id текущего пользователя. Если не зареган, выдает 0"""
    if current_user.is_authenticated:
        return current_user.id
    else:
        return 0


def get_registred_image():
    """Получение изображения профиля пользователя. Если не зареган, выдает billy.jpg"""
    if current_user.is_authenticated:
        if current_user.profile_image:
            return current_user.profile_image
        else:
            return "billy.jpg"
    else:
        return "billy.jpg"


def get_is_admin():
    """Является ли текущий пользователь админом или нет"""
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
    """Базовая страница сайта"""
    try:
        # Загружаем новости и мероприятия
        events = open('data/actual_events.json', encoding='utf-8')
        f = events.read()
        new_afisha_data = []
        afisha_data = json.loads(f)
        if afisha_data:
            afisha_data = afisha_data[::-1]  # переворачиваем, чтобы сверху отображались последние мероприятия
        for i in afisha_data:
            if not i["is_in_archive"]:
                new_afisha_data.append(i)  # создаем новый список с афишей, чтобы исключить мероприятия из архива
        na = open('data/news_articles.json', encoding='utf-8')
        f1 = na.read()
        na1 = json.loads(f1)
        new_na = []
        for k in na1:
            if not k["is_in_archive"]:
                new_na.append(k)  # Аналогично с new_afisha_data
        if na1:
            na1 = na1[::-1]  # Аналогично
        session = db_session.create_session()
        for event in afisha_data:
            # Заменяем id изображения на путь к изображению
            image = session.query(Images).filter(Images.id == event['image']).first()
            event['image'] = f"static/images/{image.file_name}"
        return render_template('./index.html',
                               afisha=afisha_data,
                               news=na1, not_registered=get_registred_id(), profile_image=get_registred_image(),
                               is_admin=get_is_admin())
    except Exception as err:
        # Здесь и далее: если случилась ошибка, отправляем пользователя на страницу с ошибкой
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/support')
def support():
    """Страница поддержки"""
    try:
        return render_template('support.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/about')
def about():
    """Страница о концерте"""
    try:
        return render_template('about.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/contacts')
def contacts():
    """Страница контакты"""
    try:
        return render_template('contacts.html', not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/archive')
def archive():
    """Страница архив концертов"""
    try:
        # Загружаем концерты
        conc = open('data/concerts.json', encoding='utf-8')
        f = conc.read()
        concerts = json.loads(f)
        if concerts:
            concerts = concerts[::-1]  # переворачиваем, чтобы сверху отображались последние
        session = db_session.create_session()
        for event in concerts:
            # Заменяем id видео, аудио и изображений на путь к ним
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
            image = session.query(Images).filter(Images.id == event['afisha_image']).first()
            try:
                event['afisha_image'] = f"static/images/{image.file_name}"
            except Exception as err:
                print(err)
        return render_template('archive.html', concerts=concerts, not_registered=get_registred_id(),
                               profile_image=get_registred_image(), is_admin=get_is_admin())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/actual_events')
def actual_events():
    """Страница актуальные мероприятия"""
    try:
        # Загружаем мероприятия
        events = open('data/actual_events.json', encoding='utf-8')
        f = events.read()
        session = db_session.create_session()

        afisha_data = json.loads(f)
        if afisha_data:
            afisha_data = afisha_data[::-1]  # переворачиваем, чтобы сначала отображались последние

        for event in afisha_data:
            # Заменяем id изображения на путь к изображению
            image = session.query(Images).filter(Images.id == event['image']).first()
            event['image'] = f"static/images/{image.file_name}"

        return render_template('actual_events.html', not_registered=get_registred_id(),
                               profile_image=get_registred_image(), afisha=afisha_data)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    try:
        # Получаем пользователя с profile_id
        profile_id = int(profile_id)
        session = db_session.create_session()
        user = session.query(Users).filter(Users.id == profile_id).first()
        data = []
        if user:
            # получаем данные пользователя
            for key in CONVERT_TO_RUSSIAN.keys():
                exec(f'data.append(((CONVERT_TO_RUSSIAN[key] + ":"), user.{key}))')
            # получаем изображения пользователя
            images = session.query(Images).filter(Images.author_id == profile_id).all()
            data1 = []
            for i in images:
                if i.operation_type == "EXIST":
                    data1.append((i.file_name, i.id, i.date, i.operation_type))  # Если изображение существует,
                    # добавляем данные о нем
            # Аналогично для видео и аудио
            videos = session.query(Videos).filter(Videos.author_id == profile_id).all()
            data2 = []
            for i in videos:
                if i.operation_type == "EXIST":
                    data2.append((i.file_name, i.id, i.date))

            audio = session.query(Audios).filter(Audios.author_id == profile_id).all()
            data3 = []

            for i in audio:
                if i.operation_type == "EXIST":
                    data3.append((i.file_name, i.id, i.date))

            if user.profile_image:
                image_profile = user.profile_image
            else:
                image_profile = "billy.jpg"
            # Проверка на возможность редактировать страницу если текущий пользователь админ или владелец профиля
            this_user = False
            if current_user.is_authenticated:
                if current_user.id == user.id:
                    this_user = True
            return render_template('profile.html', name=user.username, not_registered=get_registred_id(),
                                   user_information=data, profile_image=image_profile, image_information=data1,
                                   video_information=data2, audio_information=data3, this_user=this_user,
                                   user_id=profile_id,
                                   is_curr_user_admin=get_is_admin())
        else:
            # Если пользователя с profile_id нет, отправляем на страницу предупреждения
            return render_template('nt_exist.html', id=profile_id, type="Пользователя",
                                   not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/test')
def test():
    """ТЕСТ"""
    session = db_session.create_session()
    return "test"


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """Регистрация"""
    try:
        # проверка на регистрацию, если зареган - то выгнать со страницы
        if current_user.is_authenticated:
            return redirect("/")
        form = RegistrationForm()
        errors = []
        if form.validate_on_submit():
            session = db_session.create_session()
            new_user_name = form.username.data
            # проверки на уникальность
            users = session.query(Users).filter(Users.username == new_user_name).first()
            if users:
                errors.append("Пользователь с таким именем уже существует.")
            else:
                new_user_email = form.email.data
                users = session.query(Users).filter(Users.email == new_user_email).first()
                if users:
                    errors.append("Пользователь с такой почтой уже существует.")
                else:
                    # создаем нового пользователя
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
    """вход"""
    try:
        # проверка на регистрацию, если зареган - то выгнать со страницы
        if current_user.is_authenticated:
            return redirect("/")
        form = LoginForm()
        errors = []
        if form.validate_on_submit():
            # проверяем на правильность имени и пароля
            session = db_session.create_session()
            user = session.query(Users).filter(Users.username == form.username.data).first()
            if user:
                if check_password_hash(user.password_hash, form.password.data):
                    # если норм, то входим
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
    """Оправка пользователя на свою страницу"""
    cur_id = current_user.id
    return redirect(f"profile/{cur_id}")


@app.route('/logout')
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return redirect("/")


@app.route('/delete_from_<string:redirto>/<string:typ>/<int:del_id>')
@login_required
def delete_from(redirto, typ, del_id):
    """Удаление материалов, redirto - откуда, typ - тип удаляемого ("image", "video", "audio"), id - id удаляемого """
    try:
        session = db_session.create_session()
        redirto = str(redirto)
        if typ == "image":
            # Получаем изображение по id
            image = session.query(Images).filter(Images.id == del_id).first()
            if image:
                if (image.author_id == current_user.id) or get_is_admin():  # Если удаляет загрузивший или админ,
                    # то удаляем и присваиваем статус "DELETED"
                    image.operation_type = "DELETED"
                    try:
                        os.remove('static/images/' + image.file_name)
                    except Exception as err:
                        print(err)
        # Аналогично
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
            # если с профиля, то возвращаем назад на профиль с id
            past = redirto[redirto.find("_") + 1:]

            return redirect(f"/profile/{past}")
        else:
            return redirect("/")
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/load/image/<type>', methods=['GET', 'POST'])
@login_required
def load_image(type):
    """Загрузка изображения, type = ("prf", "adm")"""
    try:
        form = UploadFormImage()
        errors = []
        session = db_session.create_session()
        form_title = ""
        # определяем для чего загружаем, если для профиля, то type должен быть равным "prf"
        if type == "prf":
            form_title = "профиля"
        if type == "adm":
            if get_is_admin():
                form_title = "использования в материалах сайта"
            else:
                return redirect("/")

        if form.validate_on_submit():
            # Проверяем на уникальность
            images = session.query(Images).filter(Images.file_name == form.file.data.filename,
                                                  Images.operation_type == "Exist").first()
            if not images:
                form.file.data.save('static/images/' + form.file.data.filename)
                user = session.query(Users).filter(Users.id == current_user.id).first()
                if user:
                    if type == "prf":  # если для профиля, то изменяем profile_image у user, и удаляем старую аватарку
                        if user.profile_image and not get_is_admin():
                            image = session.query(Images).filter(Images.file_name == user.profile_image).first()
                            if image:
                                image.operation_type = "DELETED"
                                try:
                                    os.remove('static/images/' + user.profile_image)
                                except Exception as err:
                                    print(err)
                    # Создаем новое изображение
                    last_image = session.query(Images).order_by(Images.id.desc()).first()
                    image = Images()
                    image.id = last_image.id + 1
                    image.file_name = form.file.data.filename
                    image.operation_type = "EXIST"
                    image.date = (str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%H:%M:%S")))
                    image.author_id = user.id
                    session.merge(image)
                    if type == "prf":
                        user.profile_image = form.file.data.filename  # изменяем profile_image у user
                    session.commit()
                    return redirect("/my_profile")
            else:
                errors.append("Изображение с таким именем уже существует.")

        return render_template("load_image.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(),
                               profile_image=get_registred_image(), title=form_title)
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route('/load/video', methods=['GET', 'POST'])
@login_required
def load_video():
    """Загрузка видео"""
    try:
        # Аналогично с load_image, только без изображения профиля
        form = UploadFormVideo()
        errors = []
        session = db_session.create_session()
        if not get_is_admin():  # если не админ, то выгоняем со страницы
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
    """Загрузка аудио"""
    try:
        # аналогично с load_video
        form = UploadFormAudio()
        errors = []
        session = db_session.create_session()
        if not get_is_admin():  # если не админ, то выгоняем со страницы
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
    """Отправление новости или мероприятия в архив, typ = ("event", "article")"""
    try:
        if not get_is_admin():
            return redirect("/")  # если не админ, то выгоняем со страницы

        if typ == "event":
            # Загружаем события
            events = open('data/actual_events.json', encoding='utf-8')
            f = events.read()
            afisha_data = json.loads(f)
            for k in afisha_data:  # перебираем все новости
                if id == k['id']:
                    k['is_in_archive'] = True  # Если нашли новость, то устанавливаем параметр is_in_archive на true
            events.close()
            events = open('data/actual_events.json', 'w', encoding='utf-8')
            json.dump(afisha_data, events, ensure_ascii=False)  # сбрасываем json обратно в файл
            events.close()
        if typ == "article":
            # аналогично с событиями
            na = open('data/news_articles.json', encoding='utf-8')
            f1 = na.read()
            na1 = json.loads(f1)
            for k in na1:
                if id == k['id']:
                    k['is_in_archive'] = True
            na.close()
            na = open('data/news_articles.json', 'w', encoding='utf-8')
            json.dump(na1, na, ensure_ascii=False)
            na.close()
        return redirect("/")
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image)


@app.route("/add_event", methods=['GET', 'POST'])
@login_required
def add_event():
    """Добавить событие"""
    try:
        form = CreateEvent()
        errors = []
        session = db_session.create_session()

        if not get_is_admin():
            return redirect("/")  # если не админ, то выгоняем со страницы

        if form.validate_on_submit():
            try:
                int(form.image.data)
                images = session.query(Images).filter(Images.id == form.image.data)
                # Если изображение существует
                if images:
                    # Считываем события
                    events = open('data/actual_events.json', encoding='utf-8')
                    f = events.read()
                    afisha_data = json.loads(f)
                    # создаем новое событие
                    new_event = {}
                    try:
                        new_event["id"] = afisha_data[-1]["id"] + 1  # Находим последнее событие, присваиваем событию id
                        # равное id последнему плюс один
                    except Exception:
                        new_event["id"] = 1  # Если событий нет, то присваиваем id, равное 1
                    new_event['title'] = form.title.data
                    new_event['description'] = form.description.data
                    new_event['image'] = form.image.data
                    new_event['location'] = form.location.data
                    new_event['ticket_link'] = form.ticket_link.data
                    new_event['is_in_archive'] = False
                    new_event['author_id'] = current_user.id
                    afisha_data.append(new_event)  # добавляем в json
                    events.close()
                    events = open('data/actual_events.json', 'w', encoding='utf-8')
                    json.dump(afisha_data, events, ensure_ascii=False)  # Сбрасываем на диск
                    events.close()
                    return redirect("/")
                else:
                    errors.append("Изображения не существует")
            except Exception:
                errors.append("Id изображения должно быть числом")

        return render_template("create_event.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route("/add_news", methods=['GET', 'POST'])
@login_required
def add_news():
    """Создание новости"""
    try:
        # Аналогично с add_event
        form = CreateNews()
        errors = []
        if not get_is_admin():
            return redirect("/")
        if form.validate_on_submit():
            na = open('data/news_articles.json', encoding='utf-8')
            f1 = na.read()
            na1 = json.loads(f1)

            new_news = {}

            try:
                new_news["id"] = na1[-1]["id"] + 1
            except Exception:
                new_news["id"] = 1

            new_news['content'] = form.description.data
            new_news['title'] = form.title.data
            new_news['is_in_archive'] = False
            new_news['date'] = (str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%H:%M:%S")))
            na1.append(new_news)
            na.close()
            na = open('data/news_articles.json', 'w', encoding='utf-8')
            json.dump(na1, na, ensure_ascii=False)
            na.close()
            return redirect("/")
        return render_template("create_news.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


@app.route("/add_concert", methods=['GET', 'POST'])
@login_required
def add_concert():
    """Создаем концерт"""
    try:
        # Аналогично с add_news
        form = CreateConcert()
        if not get_is_admin():
            return redirect("/")
        errors = []
        session = db_session.create_session()

        if form.validate_on_submit():
            # Проверяем на существование видео, аудио и изображений, также на корректность введенных данных
            try:
                int(form.afisha_image.data)
                images = session.query(Images).filter(Images.id == form.afisha_image.data)
                if not images:
                    raise Exception
            except Exception:
                errors.append("Неверно указан id изображения или оно не существует")
            try:
                int(form.video_file.data)
                video = session.query(Videos).filter(Videos.id == form.video_file.data)
                if not video:
                    raise Exception
            except Exception:
                errors.append("Неверно указан id видео или оно не существует")
            try:
                int(form.audio_file.data)
                audio = session.query(Audios).filter(Audios.id == form.audio_file.data)
                if not audio:
                    raise Exception
            except Exception:
                errors.append("Неверно указан id аудио или оно не существует")

            conc = open('data/concerts.json', encoding='utf-8')
            f = conc.read()
            concerts = json.loads(f)
            conc.close()
            new_concert = {}
            try:
                new_concert["id"] = concerts[-1]["id"]
            except Exception:
                new_concert["id"] = 1
            new_concert['title'] = form.title.data
            new_concert['afisha_image'] = form.afisha_image.data
            new_concert['date_time'] = form.date_time.data
            new_concert['location'] = form.location.data
            new_concert['audio_file'] = form.audio_file.data
            new_concert['video_file'] = form.video_file.data
            concerts.append(new_concert)
            conc = open('data/concerts.json', "w", encoding='utf-8')
            json.dump(concerts, conc, ensure_ascii=False)
            conc.close()
            return redirect("/archive")
        return render_template("create_concert.html", form=form, additional_errors=errors,
                               not_registered=get_registred_id(), profile_image=get_registred_image())
    except Exception as err:
        return render_template("error.html", err=err, not_registered=get_registred_id(),
                               profile_image=get_registred_image())


if __name__ == '__main__':
    # Запускаем сервер
    app.run(port=PORT, host=SERVER)
