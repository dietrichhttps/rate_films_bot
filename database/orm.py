from database.database import sync_engine, session_factory
from database.models import Film, Rating, User, Review, Base


# Класс для создания таблицы
class TableORM:
    @staticmethod
    def create_tables():
        Base.metadata.drop_all(sync_engine)
        sync_engine.echo = False
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = False


# Класс для работы с таблицей 'users'
class UserORM:
    @staticmethod
    def get_user_id(tg_id: int) -> int | None:
        with session_factory() as session:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            return user.id if user else None

    @staticmethod
    def set_user(tg_id: int, user_name: str) -> None:
        with session_factory() as session:
            new_user = User(tg_id=tg_id, user_name=user_name)
            session.add(new_user)
            session.commit()


# Класс для работы с таблицей 'films'
class FilmORM:
    @staticmethod
    def get_or_create_film(title: str, wiki_link: str) -> int:
        with session_factory() as session:
            # Пытаемся получить объект фильма по ссылке
            film = session.query(Film).filter_by(wiki_link=wiki_link).first()
            if film:
                return film.id
            else:
                # Если фильм не найден, создаем новый объект фильма
                new_film = Film(title=title, wiki_link=wiki_link)
                session.add(new_film)
                session.commit()
                return new_film.id

    @staticmethod
    def get_all_films() -> dict[int, str] | None:
        with session_factory() as session:
            films = session.query(Film).all()
            return {film.id: film.title for film in films}

    @staticmethod
    def get_film(film_id: int) -> Film:
        with session_factory() as session:
            return session.query(Film).get(film_id)


# Класс для работы с таблицей 'ratings'
class RatingORM:
    @staticmethod
    def get_rating(film_id: int) -> int | None:
        with session_factory() as session:
            rating_obj = session.query(Rating).get(film_id)
            return rating_obj.rating if rating_obj else None

    @staticmethod
    def set_or_update_rating(user_id: int,
                             film_id: int, new_rating: int) -> None:
        with session_factory() as session:
            # Пытаемся получить объект оценки пользователя для данного фильма
            rating = session.query(Rating).filter_by(user_id=user_id,
                                                     film_id=film_id).first()
            if rating:
                # Если оценка уже существует, обновляем ее
                rating.rating = new_rating
            else:
                # Если оценка не существует, создаем новую
                new_rating_obj = Rating(user_id=user_id, film_id=film_id,
                                        rating=new_rating)
                session.add(new_rating_obj)
            session.commit()


# Класс для работы с таблицей 'reviews'
class ReviewORM:
    @staticmethod
    def get_review(film_id: int) -> int | None:
        with session_factory() as session:
            review_obj = session.query(Review).get(film_id)
            return review_obj.review if review_obj else None

    @staticmethod
    def set_review(user_id: int, film_id: int, new_review: int) -> None:
        with session_factory() as session:
            # Пытаемся получить объект рецензии пользователя для данного фильма
            review_obj = session.query(Review).filter_by(
                user_id=user_id,
                film_id=film_id).first()
            if review_obj:
                # Если оценка уже существует, обновляем ее
                review_obj.review = new_review
            else:
                # Если оценка не существует, создаем новую
                new_rating_obj = Review(user_id=user_id, film_id=film_id,
                                        review=new_review)
                session.add(new_rating_obj)
            session.commit()
