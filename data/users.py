from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

import datetime



class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    registration_date = Column(DateTime, default=datetime.datetime.now)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    profile_image = Column(String(200))
    bio = Column(Text)

    posts = orm.relationship("Posts", back_populates='users')

    def __repr__(self):
        return f"<Users(username='{self.username}', email='{self.email}')>"