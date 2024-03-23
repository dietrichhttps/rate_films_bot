import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from lexicon.lexicon import LEXICON
from filters.filters import IsRate
from services.film_service import search_films
from keyboards.films_kb import create_suggestions_keyboard
from keyboards.rates_kb import create_rates_keyboard

from database.orm import FilmORM, RateORM

router = Router()
storage = MemoryStorage()
logger = logging.getLogger(__name__)


class FSMRateFilm(StatesGroup):
    send_title = State()
    send_rate = State()


class FSMReviewFilm(StatesGroup):
    send_title = State()
    send_review = State()


class FSMFilmsData(StatesGroup):
    my_rates = State()
    my_films = State()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду /rate_film
@router.message(Command(commands='rate_film'), StateFilter(default_state))
async def process_rate_film_command(message: Message, state: FSMContext):
    await message.answer('Пришлите название фильма для оценки')
    await state.set_state(FSMRateFilm.send_title)


# Этот хэндлер будет срабатывать на текст с названием фильма
@router.message(StateFilter(FSMRateFilm.send_title))
async def process_film_title_sent(message: Message, state: FSMContext):
    logger.debug('Inside process_film_title_sent')
    query_title = message.text
    suggestions = search_films(query_title)

    if suggestions:
        await state.update_data(suggestions=suggestions)
        await message.answer(
            text='Выберите фильм',
            reply_markup=create_suggestions_keyboard(suggestions)
        )
    else:
        await message.answer('К сожалению, по вашему запросу ничего найдено')


# Этот хэндлер будет срабатаывать при нажатие на кнопку с предложенным
# фильмом
@router.callback_query(StateFilter(FSMRateFilm.send_title),
                       F.data.startswith('suggestion-'))
async def process_suggestion_press(callback: CallbackQuery, state: FSMContext):
    title = callback.data.split('suggestion-')[1]
    temp_data = await state.get_data()
    wiki_link = temp_data['suggestions'][title]
    await state.update_data(title=title, wiki_link=wiki_link, suggestions=None)

    await callback.message.answer(
        text='Отправьте оценку',
        reply_markup=create_rates_keyboard()
    )
    await callback.answer()
    await state.set_state(FSMRateFilm.send_rate)


# Этот хэндлер будет срабатывать на оценку фильма
@router.callback_query(StateFilter(FSMRateFilm.send_rate), IsRate())
async def process_film_rate_sent(callback: CallbackQuery, state: FSMContext):
    rate = int(callback.data.split('rate-')[1])
    await state.update_data(rate=rate)

    await callback.message.answer('Оценка принята!')
    await callback.answer()

    film_data = await state.get_data()
    film_data.pop('suggestions', None)
    title, wiki_link, rate = film_data.values()

    FilmORM.set_film(title, wiki_link)
    film_id = FilmORM.get_film_id(wiki_link)
    RateORM.set_rating(film_id, rate)
    await state.clear()


# Этот хэндлер будет срабатывать, если во время отправки
# оценки будет введенено что-то не то
@router.message(StateFilter(FSMRateFilm.send_rate))
async def warning_not_rate(message: Message):
    await message.answer(
        text='Оценка должна быть по 10 балльной шкале\n\n'
             'Попробуйте еще раз!')

