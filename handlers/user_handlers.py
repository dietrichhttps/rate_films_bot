import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from lexicon.lexicon import LEXICON
from filters.filters import IsRating
from services.film_service import search_films
from keyboards.films_kb import (create_suggestions_keyboard,
                                create_film_info_keyboard,
                                create_my_films_keyboard,
                                create_all_my_films_keyboard)
from keyboards.ratings_kb import create_ratings_keyboard

from database.orm import FilmORM, RatingORM

router = Router()
storage = MemoryStorage()
logger = logging.getLogger(__name__)


# Группа состояний для команды /rate_film
class FSMRateFilm(StatesGroup):
    send_title = State()
    send_rating = State()


# Группа состояний для команды /review_film
class FSMReviewFilm(StatesGroup):
    send_title = State()
    send_review = State()


# Группа состояний для команды /my_films
class FSMMyFilms(StatesGroup):
    my_films = State()
    my_ratings = State()


# Класс, содержащий обработчики для команды /start
class StartCommandHandler:
    # Этот хэндлер будет срабатывать на команду "/start" -
    # добавлять пользователя в базу данных, если его там еще не было
    # и отправлять ему приветственное сообщение
    @router.message(CommandStart(), StateFilter(default_state))
    async def process_start_command(message: Message):
        await message.answer(LEXICON[message.text])


# Класс, содержащий обработчики для команды /rate_film
class RateFilmCommandHandler:
    # Этот хэндлер будет срабатывать на команду /rate_film
    @router.message(Command(commands='rate_film'), StateFilter(default_state))
    async def process_rate_film_command(message: Message, state: FSMContext):
        await message.answer('Пришлите название фильма для оценки')
        await state.set_state(FSMRateFilm.send_title)

    # Этот хэндлер будет срабатывать на текст с названием фильма
    # после команды /rate_film
    @router.message(StateFilter(FSMRateFilm.send_title))
    async def process_film_title_sent(message: Message, state: FSMContext):
        query_title = message.text
        suggestions = search_films(query_title)

        if suggestions:
            await state.update_data(suggestions=suggestions)
            await message.answer(
                text='Выберите фильм',
                reply_markup=create_suggestions_keyboard(suggestions)
            )
        else:
            await message.answer(
                text='К сожалению, по вашему запросу ничего найдено')

    # Этот хэндлер будет срабатаывать при нажатие
    # на кнопку с предложенным фильмом
    @router.callback_query(StateFilter(FSMRateFilm.send_title),
                           F.data.startswith('suggestion-'))
    async def process_suggestion_press(callback: CallbackQuery,
                                       state: FSMContext):
        title = callback.data.split('suggestion-')[1]
        temp_data = await state.get_data()
        wiki_link = temp_data['suggestions'][title]
        await state.update_data(title=title, wiki_link=wiki_link,
                                suggestions=None)

        await callback.message.edit_text(
            text='Отправьте оценку',
            reply_markup=create_ratings_keyboard()
        )
        await callback.answer()
        await state.set_state(FSMRateFilm.send_rating)

    # Этот хэндлер будет срабатывать на нажатую кнопку с оценкой фильма
    @router.callback_query(StateFilter(FSMRateFilm.send_rating), IsRating())
    async def process_film_rating_sent(callback: CallbackQuery,
                                       state: FSMContext):
        rating = int(callback.data.split('rating-')[1])
        await state.update_data(rating=rating)

        await callback.answer('Оценка принята!')
        await callback.answer()

        film_data = await state.get_data()
        film_data.pop('suggestions', None)
        title, wiki_link, rating = film_data.values()

        FilmORM.set_film(title, wiki_link)
        film_id = FilmORM.get_film_id(wiki_link)
        RatingORM.set_rating(film_id, rating)
        await state.clear()

    # Этот хэндлер будет срабатывать, если во время отправки
    # оценки будет введенено что-то не то
    @router.callback_query(StateFilter(FSMRateFilm.send_rating))
    async def warning_not_rating(callbback: CallbackQuery):
        await callbback.answer(
            text='Оценка должна быть по 10 балльной шкале\n\n'
                 'Попробуйте еще раз!')


# Класс, содержащий обработчики для команды /my_films
class MyFilmsCommandHandler:
    # Этот хэндлер будет срабатывать на команду /my_films
    @router.message(Command(commands='my_films'), StateFilter(default_state))
    async def process_my_films_command(message: Message, state: FSMContext):
        await state.set_state(FSMMyFilms.my_films)
        await message.answer(
            text='Выберите категорию',
            reply_markup=create_my_films_keyboard()
        )

    # Этот хэндлер будет срабатывать при нажатии на кнопку "Все фильмы"
    @router.callback_query(StateFilter(FSMMyFilms.my_films),
                           F.data == 'all_films')
    async def process_all_films_press(callback: CallbackQuery,
                                      state: FSMContext):
        films = FilmORM.get_all_films()

        if films:
            await callback.message.edit_text(
                text='Список ваших фильмов',
                reply_markup=create_all_my_films_keyboard(films)
            )
            await callback.answer()
        else:
            await callback.answer('У вас пока нет фильмов')

    # Этот хэндлер будет срабатывать на нажатие фильма в категории "Все фильмы"
    @router.callback_query(StateFilter(FSMMyFilms.my_films),
                           F.data.startswith('my_film-'))
    async def process_my_film_press(callback: CallbackQuery):
        film_id = int(callback.data.split('my_film-')[1])
        title = FilmORM.get_film(film_id).title
        await callback.message.edit_text(
            text=title,
            reply_markup=create_film_info_keyboard()
        )
        await callback.asnwer()

    # Этот хэндлер будет срабатывать на нажатие кнопки "Оценка" в категории
    # create_film_info_keyboard
    @router.callback_query(StateFilter(FSMMyFilms.my_films),
                           F.data == 'my_film_rating')
    async def process_my_films_rating_press(callback: CallbackQuery):
        pass
