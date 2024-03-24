from sqlalchemy import Column, Integer, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from database.database import Base

# Создаем таблицу для связи между фильмами и оценками
film_rating_association = Table(
    'film_rating_association', Base.metadata,
    Column('film_id', Integer, ForeignKey('films.id')),
    Column('rating_id', Integer, ForeignKey('ratings.id')),
)


class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    wiki_link = Column(Text)

    # Определяем отношение "много ко многим" к оценкам
    rates = relationship('Rate', secondary=film_rating_association,
                         back_populates='films')


class Rate(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer)

    # Определяем отношение "много ко многим" к книгам
    films = relationship('Film', secondary=film_rating_association,
                         back_populates='ratings')
