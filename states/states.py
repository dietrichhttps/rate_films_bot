from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()

help_state = State()


# Группа состояний для стартового меню
class FSMStartMenu(StatesGroup):
    start_menu = State()


# Группа состояний для главного меню
class FSMMainMenu(StatesGroup):
    main_menu = State()


# Группа состояний для команды для меню оценки
class FSMRateFilmMenu(StatesGroup):
    send_title = State()
    select_suggestion = State()
    send_rating = State()
    rate_submit = State()


# Группа состояний для меню рецензии
class FSMReviewFilmMenu(StatesGroup):
    send_title = State()
    select_suggestion = State()
    send_review = State()
    submit_or_edit_review = State()


# Группа состояний для меню моих фильмов
class FSMMyFilmsMenu(StatesGroup):
    my_films = State()
    my_ratings = State()
