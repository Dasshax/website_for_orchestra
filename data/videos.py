from sqlalchemy import Column, Integer, String, DateTime
from .db_session import SqlAlchemyBase


class Videos(SqlAlchemyBase):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(50), unique=True, nullable=False)
    operation_type = Column(String(50), nullable=False)
    date = Column(DateTime, unique=False, nullable=False)

    def __repr__(self):
        return f"<Video(file_name='{self.file_name}', date='{self.date}')>"