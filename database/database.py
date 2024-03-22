from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from database.db_config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False
)

session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass
