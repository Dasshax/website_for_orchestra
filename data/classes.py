from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя:', validators=[DataRequired(message=
                                                                         "Имя пользователя не должно быть пустым!")])
    email = StringField('Email:', validators=[DataRequired(message="Почта не должна быть пустой!"),
                                              Email(message="Некорректный адресс почты")])
    password = PasswordField('Пароль:', validators=[DataRequired(message="Поле не должно быть пустым")])
    confirm_password = PasswordField('Подтвердите пароль:', validators=[
        DataRequired(message="Поле не должно быть пустым"), EqualTo('password', message="Пароли не совпадают")])
    first_name = StringField('Имя:', validators=[DataRequired(message="Поле не должно быть пустым")])
    last_name = StringField('Фамилия:', validators=[DataRequired(message="Поле не должно быть пустым")])
    bio = TextAreaField('О себе: ', validators=[])
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message="Поле не должно быть пустым")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Поле не должно быть пустым")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Вход')


class UploadFormImage(FlaskForm):
    file = FileField(validators=[FileRequired(message="Требуется файл"), FileAllowed(
        ['jpg', 'png'], 'Используйте следующие форматы: jpg, png')])
    submit = SubmitField('Загрузить')


class UploadFormVideo(FlaskForm):
    file = FileField(validators=[FileRequired(message="Требуется файл"), FileAllowed(
        ['mp4'], 'Используйте следующий формат: mp4')])
    submit = SubmitField('Загрузить')


class UploadFormAudio(FlaskForm):
    file = FileField(validators=[FileRequired(message="Требуется файл"), FileAllowed(
        ['wav', 'mp3'], 'Используйте следующие форматы: wav, mp3')])
    submit = SubmitField('Загрузить')


class CreateEvent(FlaskForm):
    title = StringField('Название:', validators=[DataRequired("Заполните это поле")])
    description = TextAreaField('Описание:', validators=[DataRequired("Заполните это поле")])
    image = IntegerField("Id изображения:", validators=[DataRequired("Заполните это поле")])
    location = StringField("Место:", validators=[DataRequired("Заполните это поле")])
    ticket_link = StringField("Ссылка на билеты:", validators=[DataRequired("Заполните это поле")])
    submit = SubmitField('Создать')


class CreateNews(FlaskForm):
    title = StringField('Название:', validators=[DataRequired("Заполните это поле")])
    description = TextAreaField('Описание:', validators=[DataRequired("Заполните это поле")])
    submit = SubmitField('Создать')


class CreateConcert(FlaskForm):
    title = StringField('Название:', validators=[DataRequired("Заполните это поле")])
    afisha_image = IntegerField("Id изображения:", validators=[DataRequired("Заполните это поле")])
    date_time = StringField('Время концерта:', validators=[DataRequired("Заполните это поле")])
    location = StringField('Место концерта:', validators=[DataRequired("Заполните это поле")])
    audio_file = IntegerField("Id аудио файла:", validators=[DataRequired("Заполните это поле")])
    video_file = IntegerField("Id видео:", validators=[DataRequired("Заполните это поле")])
    submit = SubmitField('Создать')