import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from lexicon.lexicon import LEXICON
from filters.filters import IsRating
from services.film_service import search_films
from keyboards.keyboards import MainMenu, RateFilmMenu, MyFilmsMenu, StartMenu
from database.orm import FilmORM, RatingORM
from states.states import (FSMMainMenu, FSMRateFilmMenu, FSMMyFilmsMenu,
                           FSMStartMenu)
from states.state_management import StateLinkedList

router = Router()
logger = logging.getLogger(__name__)
state_list = StateLinkedList()


# Класс, содержащий обработчики для команды /start
class StartCommandHandler:
    # Этот хэндлер будет срабатывать на команду "/start" -
    # добавлять пользователя в базу данных, если его там еще не было
    # и отправлять ему приветственное сообщение
    @router.message(CommandStart(), StateFilter(default_state))
    async def process_start_command(message: Message, state: FSMContext):
        current_state = FSMStartMenu.start_menu
        state_list.add_state(current_state)
        text = LEXICON[message.text]
        reply_markup = StartMenu.create_start_menu_kb
        message_data = (text, reply_markup)
        state_data = {'message_data': message_data}
        await state.update_data(start_menu=state_data)
        await state.set_state(FSMStartMenu.start_menu)

        await message.answer(
            text=text,
            reply_markup=reply_markup())


# Класс, содержащий обработчик команды /main_menu
class MainMenuCommandHandler:
    # Этот хэндлер будет срабатывать на команду /main_menu
    @router.callback_query(F.data == 'main_menu',
                           StateFilter(FSMStartMenu.start_menu))
    async def process_main_menu_command(callback: CallbackQuery,
                                        state: FSMContext):
        # Текст над клавиатурой
        text = 'Главное меню'
        # Ссылка на клавиатуру
        reply_markup = MainMenu.create_main_menu_kb
        # Данные для формирования ответа пользователю
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Данные текущего состояния
        state_data = {'message_data': message_data}

        # Текущее состояние
        current_state = FSMMainMenu.main_menu
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Добавляем в хранилище данные текущего состония
        await state.update_data(main_menu=state_data)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователюи
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )


# Класс, содержащий обработчики для кнопки "Оценить фильм"
class RateFilmCommandHandler:
    # Этот хэндлер будет срабатывать на кнопку "Оценить фильм"
    @router.callback_query(F.data == 'rate_film',
                           StateFilter(FSMMainMenu.main_menu))
    async def process_rate_film_press(callback: CallbackQuery,
                                      state: FSMContext):
        # Текст над клавиатурой
        text = 'Пришлите название фильма для оценки'
        # Ссылка на клавиатуру
        reply_markup = RateFilmMenu.create_rate_film_menu_kb
        # Данные для формирования ответа пользователю
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Данные текущего состояния
        state_data = {'message_data': message_data}

        # Текущее состояние
        current_state = FSMRateFilmMenu.send_title
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Добавляем в хранилище данные текущего состония
        await state.update_data(send_title=state_data)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователюи
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )
        await callback.answer()

    # Этот хэндлер будет срабатывать на текст с названием фильма
    # после команды /rate_film
    @router.message(StateFilter(FSMRateFilmMenu.send_title))
    async def process_film_title_sent(message: Message, state: FSMContext):
        # Название поискового запроса
        query_title = message.text
        # Данные из хранилища
        storage_data = await state.get_data()
        # Данные из текущего состония
        select_suggestion_data = storage_data.get('select_suggestion', {})
        # Кэшированные данные текущего состояния
        cached_data = select_suggestion_data.get(
            'message_data', {}).get(
                'cached_data', {})
        # Текст над клавиатурой
        text = 'Выберите фильм'
        # Ссылка на клавиатуру
        reply_markup = RateFilmMenu.create_suggestions_menu_kb
        # Данные для формирования ответа пользователю
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Проверяем есть ли строка с поисковым запросом в
        # в ключах словаря с кэшированными данными текущего состояния
        if query_title in cached_data.keys():
            # Добавляем текущий поисковый запрос в кэшированные данные,
            # чтобы в дальнейшем доставать по нему кэшированные
            # предложения из Википедии
            cached_data['current_query_title'] = query_title
        else:
            # Получаем результаты поиска в Википедии
            suggestions = search_films(query_title)
            # Добавляем связку "поисковый запрос - предложения из Википедии"
            cached_data.setdefault(query_title, suggestions)
            # Добавляем текущий поисковый запрос в кэшированные данные,
            # чтобы в дальнейшем доставать по нему кэшированные
            # предложения из Википедии
            cached_data['current_query_title'] = query_title
            # Добавляем в словарь с данными для
            # формирования ответа кэшированные данные
            message_data.setdefault('cached_data', cached_data)
            # Добавляем в словарь с данными текущего состояния данные для
            # отправки сообщения
            state_data = {'message_data': message_data}
            # Добавляем в хранилизе данные текущего состояния
            await state.update_data(select_suggestion=state_data)

        # Определяем текущее состояние
        current_state = FSMRateFilmMenu.select_suggestion
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователю
        await message.answer(
            text=text,
            reply_markup=reply_markup(cached_data)
        )

    # Этот хэндлер будет срабатаывать при нажатии
    # на кнопку с предложенным фильмом
    @router.callback_query(StateFilter(FSMRateFilmMenu.select_suggestion),
                           F.data.startswith('suggestion-'))
    async def process_suggestion_press(callback: CallbackQuery,
                                       state: FSMContext):
        # Данные фильма
        selected_title = callback.data.split('suggestion-')[1]
        storage_data = await state.get_data()
        cached_data = (storage_data['select_suggestion']
                       ['message_data']['cached_data'])
        current_query_title = cached_data['current_query_title']
        wiki_link = cached_data[current_query_title][selected_title]
        film_data = {'title': selected_title, 'wiki_link': wiki_link}

        # Данные для отправки сообщения
        text = 'Отправьте оценку'
        reply_markup = RateFilmMenu.create_ratings_menu_kb
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Получаем словарь с данными текущего состояния
        state_data = {'message_data': message_data, 'film_data': film_data}

        # Определяем текущее состояние
        current_state = FSMRateFilmMenu.send_rating
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Добавляем данные текущего состояния в хранилище
        await state.update_data(send_rating=state_data)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )
        await callback.answer()

    # Этот хэндлер будет срабатывать на нажатую кнопку с оценкой фильма
    @router.callback_query(StateFilter(FSMRateFilmMenu.send_rating),
                           IsRating())
    async def process_film_rating_sent(callback: CallbackQuery,
                                       state: FSMContext):
        rating = int(callback.data.split('rating-')[1])

        # Получаем данные для отправки в базу данных
        storage_data = await state.get_data()
        film_data = storage_data['send_rating']['film_data']
        title, wiki_link = film_data.values()

        # Отправляем название фильма, ссылку и оценку
        # в базу данных
        FilmORM.set_film(title, wiki_link)
        film_id = FilmORM.get_film_id(wiki_link)
        RatingORM.set_rating(film_id, rating)

        # Определяем текущее состояние
        current_state = FSMRateFilmMenu.rate_complete
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователю
        await callback.answer('Оценка принята!')
        await callback.answer()


# Класс, содержащий обработчики для команды /my_films
class MyFilmsCommandHandler:
    # Этот хэндлер будет срабатывать на команду /my_films
    @router.message(Command(commands='my_films'),
                    StateFilter(FSMMainMenu.main_menu))
    async def process_my_films_command(message: Message, state: FSMContext):
        await message.answer(
            text='Выберите категорию',
            reply_markup=MyFilmsMenu.create_my_films_menu_kb()
        )
        await state.set_state(FSMMyFilmsMenu.my_films)

    # Этот хэндлер будет срабатывать при нажатии на кнопку "Все фильмы"
    @router.callback_query(StateFilter(FSMMyFilmsMenu.my_films),
                           F.data == 'all_films')
    async def process_all_films_press(callback: CallbackQuery,
                                      state: FSMContext):
        films = FilmORM.get_all_films()

        if films:
            await callback.message.edit_text(
                text='Список ваших фильмов',
                reply_markup=MyFilmsMenu.create_all_my_films_menu_kb(films)
            )
            await callback.answer()
        else:
            await callback.answer('У вас пока нет фильмов')

    # Этот хэндлер будет срабатывать на нажатие фильма в категории "Все фильмы"
    @router.callback_query(StateFilter(FSMMyFilmsMenu.my_films),
                           F.data.startswith('my_film-'))
    async def process_my_film_press(callback: CallbackQuery):
        film_id = int(callback.data.split('my_film-')[1])
        title = FilmORM.get_film(film_id).title
        await callback.message.edit_text(
            text=title,
            reply_markup=MyFilmsMenu.create_film_info_menu_kb()
        )
        await callback.answer()


# Класс, содержащий обработчики кнопок навигации
class NavigationCommandHandler:
    # Этот хэндлер будет срабатывать при нажатии кнопки "Назад"
    @router.callback_query(F.data == 'return', StateFilter(FSMRateFilmMenu))
    async def process_return_press(callback: CallbackQuery, state: FSMContext):
        # Получаем словарь из MemoryStorage()
        storage_data = await state.get_data()
        # Получаем предыдущее состояние пользователя
        state_list.go_back()
        prev_state = state_list.get_current_state_str()
        # Получаем данные для отправки сообщения
        message_data = list(
            storage_data.get(
                prev_state.split(':')[1]).get('message_data').values())
        text, reply_markup_ref = message_data[:2]
        reply_markup_arg = message_data[-1] if len(message_data) > 2 else None
        reply_markup_to_use = (reply_markup_ref(reply_markup_arg)
                               if reply_markup_arg else reply_markup_ref())

        # Отправляем клавиатуру из прошлого состояния
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup_to_use
        )

        # Возвращаем пользователя в предыдущее состояние
        await state.set_state(prev_state)

    # Этот хэндлер будет срабатывать при нажатии кнопки "Отмена"
    @router.callback_query(F.data == 'cancel', ~StateFilter(default_state))
    async def process_cancel_press(callback: CallbackQuery, state: FSMContext):
        # Получаем словарь из MemoryStorage()
        storage_data = await state.get_data()
        # Получаем данные для отправки ответа
        message_data = storage_data['start_menu']['message_data']
        text, reply_markup = message_data

        # Отправляем ответ из меню старта
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )

        # Возвращаем пользователя в состояние стартового меню
        await state.set_state(FSMStartMenu.start_menu)
