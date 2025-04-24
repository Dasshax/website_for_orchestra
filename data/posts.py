from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

import datetime


class Posts(SqlAlchemyBase):
    """Класс для таблицы Posts из бд"""
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    publication_date = Column(DateTime, default=datetime.datetime.now)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category = Column(String(50))
    image = Column(String(200))
    is_published = Column(Boolean, default=False)
    views = Column(Integer, default=0)

    user = orm.relationship('Users')

    def __repr__(self):
        return f"<Posts(title='{self.title}', author_id={self.author_id})>"
