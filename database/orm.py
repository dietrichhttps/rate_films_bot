from sqlalchemy import select, Integer, Text, func
from database.database import sync_engine, session_factory
from database.models import Film, Rate, Base


class TableORM:
    @staticmethod
    def create_tables():
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = False


class FilmORM:
    @staticmethod
    def get_film_id(wiki_link: str) -> int | None:
        with session_factory() as session:
            query = select(Film.id).filter(wiki_link == wiki_link)
            result = session.execute(query).scalar()

        return result

    @staticmethod
    def set_film(title: str, wiki_link: str) -> None:
        with session_factory() as session:
            film = Film(title=title, wiki_link=wiki_link)
            session.add(film)
            session.commit()


class RateORM:
    @staticmethod
    def set_rating(film_id: int, rate: int) -> None:
        with session_factory() as session:
            # Получаем объект фильма по его идентификатору
            film = session.query(Film).filter_by(id=film_id).first()
            if film:
                # Создаем объект оценки и присваиваем ему значение
                new_rating = Rate(rating=rate)
                # Связываем оценку с фильмом
                film.ratings.append(new_rating)
                # Добавляем новую оценку и фиксируем изменения в базе данных
                session.add(new_rating)
                session.commit()
