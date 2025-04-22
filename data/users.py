from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

import datetime

global CONVERT_TO_RUSSIAN

CONVERT_TO_RUSSIAN = {"id": "id", "username": "имя пользователя", "email": "электронная почта", "first_name": "имя",
                      "last_name": "фамилия", "registration_date": "дата регистрации", "is_admin": "администратор",
                      "bio": "о себе"}

class Users(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    registration_date = Column(String(50), default=datetime.datetime.now)
    last_login = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    profile_image = Column(String(200))
    bio = Column(Text)

    _posts = orm.relationship("Posts", backref='users')
    _videos = orm.relationship("Videos", backref='users')
    _images = orm.relationship("Images", backref='users')
    _audios = orm.relationship("Audios", backref='users')
    def __repr__(self):
        return f"<Users(username='{self.username}', email='{self.email}')>"