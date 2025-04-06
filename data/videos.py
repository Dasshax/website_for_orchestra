from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Videos(SqlAlchemyBase):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(50), unique=True, nullable=False)
    operation_type = Column(String(50), nullable=False)
    date = Column(DateTime, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = orm.relationship('Users')
    def __repr__(self):
        return f"<Video(file_name='{self.file_name}', date='{self.date}')>"