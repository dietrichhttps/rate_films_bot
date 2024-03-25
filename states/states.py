from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class FSMStartMenu(StatesGroup):
    start_menu = State()


# Группа состояний для команды /main_menu
class FSMMainMenu(StatesGroup):
    main_menu = State()


# Группа состояний для команды /rate_film
class FSMRateFilmMenu(StatesGroup):
    send_title = State()
    select_suggestion = State()
    send_rating = State()
    rate_complete = State()


# Группа состояний для команды /review_film
class FSMReviewFilmMenu(StatesGroup):
    send_title = State()
    send_review = State()


# Группа состояний для команды /my_films
class FSMMyFilmsMenu(StatesGroup):
    my_films = State()
    my_ratings = State()
