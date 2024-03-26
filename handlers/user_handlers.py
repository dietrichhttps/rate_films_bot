import logging

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from lexicon.lexicon import LEXICON
from filters.filters import IsRating
from services.film_service import search_films
from keyboards.keyboards import (MainMenu, RateReviewFilmMenu,
                                 MyFilmsMenu, StartMenu, Navigation)
from database.orm import UserORM, FilmORM, RatingORM, ReviewORM
from states.states import (FSMMainMenu, FSMRateFilmMenu, FSMMyFilmsMenu,
                           FSMStartMenu, FSMReviewFilmMenu, help_state)
from states.state_management import StateLinkedList

router = Router()
logger = logging.getLogger(__name__)
state_list = StateLinkedList()


# Класс, содержащий обработчики для команды /start
class StartCommandHandler:
    # Этот хэндлер будет срабатывать на команду "/start",
    # отправлять ему приветственное сообщение и
    # отаправлять ему клавиатуру для входа в главное меню
    @router.message(CommandStart(), StateFilter(default_state))
    async def process_start_command(message: Message, state: FSMContext):
        # Получаем данные о пользователе
        tg_id = int(message.from_user.id)
        user_name = message.from_user.full_name
        # Добавляем пользователя в БД
        UserORM.set_user(tg_id, user_name)
        # Определяем текущее состояние
        current_state = FSMStartMenu.start_menu
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Подготавливаем данные для формирования ответа
        text = LEXICON[message.text]
        reply_markup = StartMenu.create_start_menu_kb
        # Добавляем данные в словарь с данными для ответа
        message_data = {'text': text, 'reply_markup': reply_markup}
        # Добавляем словарь с данными для ответа в словарь с
        # данными текущего состояния
        state_data = {'message_data': message_data}
        # Добавляем словарь с данными текущего состония в хранилище
        await state.update_data(start_menu=state_data)
        # Устанавливаем текущее состояние
        await state.set_state(FSMStartMenu.start_menu)

        # Отправляем ответ пользователю
        await message.answer(
            text=text,
            reply_markup=reply_markup())


class HelpCommandHandler:
    @router.message(Command(commands='help'),
                    ~StateFilter(help_state))
    async def process_help_command(message: Message, state: FSMContext):
        # Текущее состояние
        current_state = state_list.get_current_state_str()
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await message.answer(
            text=LEXICON['/help'],
            reply_markup=Navigation.create_navigation_kb()
        )


# Класс, содержащий обработчики кнопок навигации
class NavigationCommandHandler:
    # Этот хэндлер будет срабатывать при нажатии кнопки "Назад"
    @router.callback_query(F.data == 'return', ~StateFilter(help_state,
                                                            default_state))
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
        text, reply_markup = message_data.values()

        # Отправляем ответ из меню старта
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )

        # Возвращаем пользователя в состояние стартового меню
        await state.set_state(FSMStartMenu.start_menu)

    # Этот хэндлер будет срабатывать при нажатии кнопки "Главное меню"
    # и при отправке команды /main_menu
    @router.message(Command(commands='main_menu'), ~StateFilter(default_state))
    @router.callback_query(F.data == 'main_menu',
                           ~StateFilter(default_state, FSMMainMenu))
    async def process_main_menu_press(update: Message | CallbackQuery = None,
                                      state: FSMContext = None):
        # Текст над клавиатурой
        text = 'Главное меню'
        # Ссылка на клавиатуру
        reply_markup = MainMenu.create_main_menu_kb
        # Данные для формирования ответа пользователю
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Данные текущего состояния
        state_data = {'message_data': message_data}

        # Добавляем состояние главного меню в список состояний,
        # если его там нет
        current_state = FSMMainMenu.main_menu
        state_list.add_state(current_state)

        # Добавляем в хранилище данные текущего состония
        await state.update_data(main_menu=state_data)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        update_type = type(update)
        if update_type == CallbackQuery:
            # Отправляем ответ из главного меню
            await update.message.edit_text(
                text='Главное меню',
                reply_markup=MainMenu.create_main_menu_kb()
            )
        elif update_type == Message:
            # Отправляем ответ из главного меню
            await update.answer(
                text='Главное меню',
                reply_markup=MainMenu.create_main_menu_kb()
            )


# Класс, содержащий обработчики для
# меню "Оценить фильм" и "Написать рецензию"
class RateReviewFilmMenuHandler:
    # Этот хэндлер будет срабатывать на кнопки "Оценить фильм"
    # и "Написать рецензию"
    @router.callback_query(F.data.in_(['rate_film', 'review_film']),
                           StateFilter(FSMMainMenu.main_menu))
    async def process_rate_review_film_press(callback: CallbackQuery,
                                             state: FSMContext):
        menu_name = callback.data
        text_words = {'rate': 'оценки', 'review': 'рецензии'}
        text_word = text_words.get(menu_name.split('_')[0])
        # Текст над клавиатурой
        text = f'Пришлите название фильма для {text_word}'
        # Ссылка на клавиатуру
        reply_markup = Navigation.create_navigation_kb
        # Данные для формирования ответа пользователю
        message_data = {'text': text, 'reply_markup': reply_markup}

        # Данные текущего состояния
        state_data = {'message_data': message_data}

        if menu_name == 'rate_film':
            # Текущее состояние
            current_state = FSMRateFilmMenu.send_title
        else:
            # Текущее состояние
            current_state = FSMReviewFilmMenu.send_title
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
    # после нажатия на кнопки "Оценить фильм" и "Написать рецензию"
    @router.message(StateFilter(FSMRateFilmMenu.send_title,
                                FSMReviewFilmMenu.send_title))
    async def process_film_title_sent(message: Message, state: FSMContext):
        prev_state = state_list.get_current_state_str()
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
        reply_markup = RateReviewFilmMenu.create_suggestions_menu_kb
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
            if suggestions:
                # Добавляем связку "поисковый запрос -
                # предложения из Википедии"
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
            else:
                await message.answer(
                    text='Изивините, по вашему запросу ничего не найдено\n'
                         'Попробуйте еще раз')
                return

        if prev_state == 'FSMRateFilmMenu:send_title':
            # Определяем текущее состояние
            current_state = FSMRateFilmMenu.select_suggestion
        else:
            # Определяем текущее состояние
            current_state = FSMReviewFilmMenu.select_suggestion
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователю
        await message.answer(
            text=text,
            reply_markup=reply_markup(cached_data)
        )

    # Этот хэндлер будет срабатывать при нажатии
    # на кнопку с предложенным фильмом
    @router.callback_query(StateFilter(FSMRateFilmMenu.select_suggestion,
                                       FSMReviewFilmMenu.select_suggestion,),
                           F.data.startswith('suggestion-'))
    async def process_suggestion_press(callback: CallbackQuery,
                                       state: FSMContext):
        prev_state = state_list.get_current_state_str()
        # Данные фильма
        selected_title = callback.data.split('suggestion-')[1]
        storage_data = await state.get_data()
        cached_data = (storage_data['select_suggestion']
                       ['message_data']['cached_data'])
        current_query_title = cached_data['current_query_title']
        wiki_link = cached_data[current_query_title][selected_title]
        film_data = {'title': selected_title, 'wiki_link': wiki_link}

        if prev_state == 'FSMRateFilmMenu:select_suggestion':
            # Данные для отправки сообщения
            text = 'Отправьте оценку'
            reply_markup = RateReviewFilmMenu.create_ratings_menu_kb
            message_data = {'text': text, 'reply_markup': reply_markup}
            # Определяем текущее состояние
            current_state = FSMRateFilmMenu.send_rating
            # Получаем словарь с данными текущего состояния
            state_data = {'message_data': message_data, 'film_data': film_data}
            # Добавляем данные текущего состояния в хранилище
            await state.update_data(send_rating=state_data)
        else:
            # Данные для отправки сообщения
            text = 'Отправьте текст рецензии'
            reply_markup = Navigation.create_navigation_kb
            message_data = {'text': text, 'reply_markup': reply_markup}
            # Определяем текущее состояние
            current_state = FSMReviewFilmMenu.send_review
            # Получаем словарь с данными текущего состояния
            state_data = {'message_data': message_data, 'film_data': film_data}
            # Добавляем данные текущего состояния в хранилище
            await state.update_data(send_review=state_data)

        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )
        await callback.answer()

    # Этот хэндлер будет срабатывать на нажатую кнопку с оценкой фильма
    @router.callback_query(StateFilter(FSMRateFilmMenu.send_rating,
                                       FSMRateFilmMenu.rate_submit),
                           IsRating())
    async def process_film_rating_sent(callback: CallbackQuery,
                                       state: FSMContext):
        # Получаем id пользователя
        user_id = UserORM.get_user_id(int(callback.from_user.id))
        # Сохраняем в переменную оценку из апдейта
        new_rating = int(callback.data.split('rating-')[1])

        # Получаем данные для отправки в базу данных
        storage_data = await state.get_data()
        film_data = storage_data['send_rating']['film_data']
        title, wiki_link = film_data.values()

        # Отправляем название фильма, ссылку и оценку
        # в базу данных
        film_id = FilmORM.get_or_create_film(title, wiki_link)
        RatingORM.set_or_update_rating(user_id, film_id, new_rating)

        # Определяем текущее состояние
        current_state = FSMRateFilmMenu.rate_submit
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователю
        await callback.answer('Оценка принята!')
        await callback.answer()

    # Этот хэндлер будет срабатывать на кнопку "Подтвердить" в меню оценки
    @router.callback_query(F.data == 'submit_rate',
                           StateFilter(FSMRateFilmMenu.rate_submit))
    async def process_rate_submit_press(callback: CallbackQuery,
                                        state: FSMContext):
        # Определяем текущее состояние
        current_state = FSMMainMenu.main_menu
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await callback.message.edit_text(
            text='Главное меню',
            reply_markup=MainMenu.create_main_menu_kb()
        )

    # Этот хэндлер будет срабатывать на отправленную рецензию
    @router.message(StateFilter(FSMReviewFilmMenu.send_review))
    async def process_film_review_sent(message: Message, state: FSMContext):
        # Сохраняем в переменную рецензию из апдейта
        review_text = message.text
        # Данные текущего состояния
        state_data = {'review_text': review_text}

        # Текущее состояние
        current_state = FSMReviewFilmMenu.submit_or_edit_review
        # Добавляем данные текущего состояния в хранилище
        await state.update_data(submit_or_edit_review=state_data)
        # Добавляем в односвязный список состояний текущее состояние
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await message.answer(
            text=f'Текст вашей рецензии:\n\n{review_text}',
            reply_markup=RateReviewFilmMenu.create_review_menu_kb()
        )

    # Этот хэндлер будет срабатывать на кнопку "Изменить" в
    # меню рецензии
    @router.callback_query(F.data == 'edit_review',
                           StateFilter(
                               FSMReviewFilmMenu.submit_or_edit_review))
    async def process_edit_review_press(callback: CallbackQuery,
                                        state: FSMContext):
        # Данные для отправки сообщения
        text = 'Отправьте рецензию'
        reply_markup = Navigation.create_navigation_kb
        # Определяем текущее состояние
        current_state = FSMReviewFilmMenu.send_review
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup()
        )

    # Этот хэндлер будет срабатывать на кнопку "Подтвердить"
    # в меню рецензии
    @router.callback_query(F.data == 'submit_review',
                           StateFilter(
                               FSMReviewFilmMenu.submit_or_edit_review))
    async def process_submit_review_press(callback: CallbackQuery,
                                          state: FSMContext):
        # Получаем id пользователя
        user_id = UserORM.get_user_id(int(callback.from_user.id))
        # Получаем данные из хранлища
        storage_data = await state.get_data()
        # Получаем текст рецензии из состояния
        # FSMReviewFilmMenu.submit_or_edit_review
        review_text = storage_data['submit_or_edit_review']['review_text']

        # Получаем данные для отправки в базу данных
        storage_data = await state.get_data()
        film_data = storage_data['send_review']['film_data']
        title, wiki_link = film_data.values()

        # Отправляем название фильма, ссылку и рецензию
        # в базу данных
        film_id = FilmORM.get_or_create_film(title, wiki_link)
        ReviewORM.set_review(user_id, film_id, review_text)

        # Определяем текущее состояние
        current_state = FSMMainMenu.main_menu
        # Добавляем текущее состояние в список состояний
        state_list.add_state(current_state)
        # Устанавливаем текущее состояние
        await state.set_state(current_state)

        # Отправляем ответ пользователю
        await callback.answer('Рецензия принята!')
        await callback.message.edit_text(
            text='Главное меню',
            reply_markup=MainMenu.create_main_menu_kb()
        )


# Класс, содержащий обработчики для команды /my_films
class MyFilmsMenuHandler:
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
