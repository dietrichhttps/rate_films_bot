from aiogram import Bot
from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup, BotCommand)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_COMMANDS


# Класс для работы с кнопками
class Buttons:
    @staticmethod
    # Функция, создающая кнопки навигации
    def create_navigation_buttons() -> list[InlineKeyboardButton]:
        navigation_buttons = [
            InlineKeyboardButton(text='Назад', callback_data='return'),
            InlineKeyboardButton(text='Отмена', callback_data='cancel'),
            InlineKeyboardButton(text='Главное меню',
                                 callback_data='main_menu')
        ]
        return navigation_buttons


# Класс, внутри которого генераторы клавиатур и кнопок
class Generator:
    # Генератор кнопок
    @staticmethod
    def create_button(text: str,
                      callback_data: str,
                      url: str = None) -> InlineKeyboardButton:
        if url:
            return InlineKeyboardButton(text=text, url=url)
        else:
            return InlineKeyboardButton(text=text, callback_data=callback_data)

    # Генератор клавиатур
    @staticmethod
    def create_keyboard(buttons: list[list[InlineKeyboardButton]],
                        row_width: int = 1) -> InlineKeyboardMarkup:
        kb_builder = InlineKeyboardBuilder()
        for row in buttons:
            kb_builder.row(*row, width=row_width)
        return kb_builder.as_markup()


# Класс, внутри которого клавиатуры навигации
class Navigation:
    # Функция, создающая клавиатуру для навигации
    @staticmethod
    def create_navigation_kb() -> InlineKeyboardMarkup:
        buttons = [
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, row_width=2)


# Функция для настройки кнопки Menu бота
async def set_default_main_menu(bot: Bot):
    default_main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command, description in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(default_main_menu_commands)


# Класс, внутри которого клавиатура для стартового меню
class StartMenu:
    # Функция, создающая клавиатуру стартового меню
    @staticmethod
    def create_start_menu_kb():
        start_btn = [
            [Generator.create_button(
                text='Старт',
                callback_data='main_menu'
            )]
        ]
        return Generator.create_keyboard(start_btn)


# Класс, внутри которого клавиатуры для главного меню
class MainMenu:
    # Функция, создающая клавиатуру главного меню
    @staticmethod
    def create_main_menu_kb() -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Оценить фильм', 'rate_film'),
             Generator.create_button('Написать рецензию', 'review_film')],
            [Generator.create_button('Мои фильмы', 'my_films')],
            [Generator.create_button('Отмена', 'cancel')]
        ]
        return Generator.create_keyboard(buttons, row_width=2)


# Класс, внутри которого клавиатуры
# для меню "Оценить фильм" и "Написать рецензию"
class RateReviewFilmMenu:
    # Функция, создающая клавиатуру для предложений из Википедии
    @staticmethod
    def create_suggestions_menu_kb(
            suggestions_data: dict) -> InlineKeyboardMarkup:
        title = suggestions_data['current_query_title']
        buttons: list[list[InlineKeyboardButton]] = []
        for title, link in suggestions_data[title].items():
            suggestion_button = Generator.create_button(
                text=title, callback_data=f'film_title-{title}')
            link_button = Generator.create_button(
                text='Ссылка на фильм', url=link, callback_data=None)
            buttons.append([suggestion_button])
            buttons.append([link_button])
        buttons.append(Buttons.create_navigation_buttons())

        return Generator.create_keyboard(buttons, 2)

    # Функция, создающая клавиатуру с оценками
    @staticmethod
    def create_ratings_menu_kb() -> InlineKeyboardMarkup:
        submit_btn = Generator.create_button(
            text='Подтвердить', callback_data='submit_rate'
        )
        buttons = [[Generator.create_button(
            str(rating),
            f'rating-{rating}') for rating in reversed(range(11))],
            [submit_btn],
            Buttons.create_navigation_buttons()
            ]
        return Generator.create_keyboard(buttons, 2)

    # Функция, создающая клавиатуру с рецензией
    @staticmethod
    def create_review_menu_kb() -> InlineKeyboardMarkup:
        edit_btn = Generator.create_button(
            text='Изменить', callback_data='edit_review'
        )
        submit_btn = Generator.create_button(
            text='Подтвердить', callback_data='submit_review'
        )
        buttons = [
            [edit_btn, submit_btn],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)


# Класс, внутри которого клавиатуры для меню со всеми фильмами
class MyFilmsMenu:
    # Функция, создающая клавиатуру для меню с моими фильмами
    @staticmethod
    def create_my_films_menu_kb() -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Все фильмы', 'all_films'),
             Generator.create_button('Фильмы по оценкам', 'films_by_rating')],
            [Generator.create_button('Поиск фильмов 🔎', 'search_my_films')],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)

    # Функция, создающая клавиатуру для меню со всеми фильмами
    @staticmethod
    def create_all_my_films_menu_kb(
            films: dict[int, str]) -> InlineKeyboardMarkup:
        # Инициализируем список для кнопок
        buttons = []

        # Создаем строку кнопок с фильмами
        film_buttons_row = []
        for film_id, title in films.items():
            film_buttons_row.append(
                Generator.create_button(title, f'my_film-{film_id}'))

            # Если набралось одна кнопку в строку, добавляем эту
            # строку в список кнопок и очищаем строку для следующей пары кнопок
            if len(film_buttons_row) == 1:
                buttons.append(film_buttons_row)
                film_buttons_row = []

        # Если в строке осталась одна кнопка, добавляем ее в список кнопок
        if film_buttons_row:
            buttons.append(film_buttons_row)

        # Добавляем кнопки навигации в отдельную строку
        buttons.append(Buttons.create_navigation_buttons())

        # Создаем клавиатуру из списка кнопок
        return Generator.create_keyboard(buttons, 2)

    # Функция, создающая клавиатуру для меню с информацией о фильме
    @staticmethod
    def create_film_info_menu_kb(url: str) -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Оценка', 'my_film_rating'),
             Generator.create_button('Рецензия', 'my_film_review')],
            [Generator.create_button('Страница в Википедии',
                                     url=url,
                                     callback_data=None)],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)

    # Функция, создающая клавитуру для меню с оценкой фильма
    @staticmethod
    def create_rating_review_menu_kb(button_text: str,
                                     button_data: str) -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button(button_text, button_data)],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)
