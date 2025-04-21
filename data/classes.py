from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from .db_session import SqlAlchemyBase

import datetime


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
    bio = StringField('О себе: ', validators=[])
    submit = SubmitField('Регистрация')


class EnterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(message="Поле не должно быть пустым")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Поле не должно быть пустым")])
    submit = SubmitField('Вход')



