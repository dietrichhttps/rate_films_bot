import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from lexicon.lexicon import LEXICON
from filters.filters import IsRate
from services.film_service import search_films
from keyboards.films_kb import create_suggestions_keyboard

router = Router()

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
    logger.debug('Inside process_start_command')
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду /rate_film
@router.message(Command(commands='rate_film'), StateFilter(default_state))
async def process_rate_film_command(message: Message, state: FSMContext):
    logger.debug('Inside process_rate_film_command')
    await message.answer('Пришлите название фильма для оценки')
    await state.set_state(FSMRateFilm.send_title)


# Этот хэндлер будет срабатывать на текст с названием фильма
@router.message(StateFilter(FSMRateFilm.send_title))
async def process_film_title_sent(message: Message, state: FSMContext):
    logger.debug('Inside process_film_title_sent')
    query_title = message.text
    suggestions = search_films(query_title)

    await message.answer(
        text='Выберите фильм',
        reply_markup=create_suggestions_keyboard(suggestions)
    )


# Этот хэндлер будет срабатаывать при нажатие на кнопку с предложенным
# фильмом
@router.callback_query(StateFilter(FSMRateFilm.send_title),
                       F.data.startswith('suggestion-'))
async def process_suggestion_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправьте оценку')
    await callback.answer()
    await state.set_state(FSMRateFilm.send_rate)


# Этот хэндлер будет срабатывать на оценку фильма
@router.message(StateFilter(FSMRateFilm.send_rate), IsRate())
async def process_film_rate_sent(message: Message, state: FSMContext):
    logger.debug('Inside process_film_rate_sent')
    await message.answer('Оценка принята!')
    await state.clear()


# Этот хэндлер будет срабатывать, если во время ввода
# названия фильма будет введено что-то некорректное
@router.message(StateFilter(FSMRateFilm.send_rate))
async def warning_not_film_title(message: Message):
    await message.answer(
        text='Оценка должна быть по 10 балльной шкале\n\n'
             'Попробуйте еще раз!')
