from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from .db_session import SqlAlchemyBase

import datetime


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль:', validators=[DataRequired(), EqualTo('password')])
    bio = StringField('О себе: ', validators=[])
    submit = SubmitField('Регистрация')


class EnterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Вход')



