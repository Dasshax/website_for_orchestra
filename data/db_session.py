import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__FACTORY = None


def global_init(db_file):
    """Функция для создания сессии для бд"""
    global __FACTORY

    if __FACTORY:
        raise Exception("Здесь этого не должно быть")

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    engine = sa.create_engine(conn_str, echo=False)
    __FACTORY = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """Функция для получения сессии"""
    global __FACTORY
    return __FACTORY()
