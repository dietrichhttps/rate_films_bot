from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Buttons:
    @staticmethod
    def create_navigation_buttons(
            with_main_menu: bool = False) -> list[InlineKeyboardButton]:
        if not with_main_menu:
            navigation_buttons = [
                InlineKeyboardButton(text='Назад', callback_data='return'),
                InlineKeyboardButton(text='Отмена', callback_data='cancel')
            ]
        else:
            navigation_buttons = [
                InlineKeyboardButton(text='Назад', callback_data='return'),
                InlineKeyboardButton(text='Главное меню',
                                     callback_data='main_menu'),
                InlineKeyboardButton(text='Отмена', callback_data='cancel')
            ]
        return navigation_buttons


class Generator:
    @staticmethod
    def create_button(text: str,
                      callback_data: str,
                      url: str = None) -> InlineKeyboardButton:
        if url:
            return InlineKeyboardButton(text=text, url=url)
        else:
            return InlineKeyboardButton(text=text, callback_data=callback_data)

    @staticmethod
    def create_keyboard(buttons: list[list[InlineKeyboardButton]],
                        row_width: int = 1) -> InlineKeyboardMarkup:
        kb_builder = InlineKeyboardBuilder()
        for row in buttons:
            kb_builder.row(*row, width=row_width)
        return kb_builder.as_markup()


class MainMenu:
    @staticmethod
    def create_main_menu_kb() -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Оценить фильм', 'rate_film'),
             Generator.create_button('Написать рецензию', 'review_film')],
            [Generator.create_button('Мои фильмы', 'my_films')],
            [Generator.create_button('Отмена', 'cancel')]
        ]
        return Generator.create_keyboard(buttons, row_width=2)


class RateFilmMenu:
    @staticmethod
    def create_rate_film_menu_kb() -> InlineKeyboardMarkup:
        buttons = [
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, row_width=2)

    @staticmethod
    def create_suggestions_kb(suggestions_data: dict) -> InlineKeyboardMarkup:
        title = suggestions_data['current_query_title']
        buttons: list[list[InlineKeyboardButton]] = []
        for title, link in suggestions_data[title].items():
            suggestion_button = Generator.create_button(
                text=title, callback_data=f'suggestion-{title}')
            link_button = Generator.create_button(
                text='Ссылка на фильм', url=link, callback_data=None)
            buttons.append([suggestion_button])
            buttons.append([link_button])
        buttons.append(Buttons.create_navigation_buttons())

        return Generator.create_keyboard(buttons, 2)

    @staticmethod
    def create_ratings_kb() -> InlineKeyboardMarkup:
        buttons = [[Generator.create_button(
            str(rating),
            f'rating-{rating}') for rating in reversed(range(11))],
            Buttons.create_navigation_buttons()
            ]
        return Generator.create_keyboard(buttons, 2)


class MyFilmsMenu:
    @staticmethod
    def create_my_films_kb() -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Все фильмы', 'all_films'),
             Generator.create_button('Фильмы по оценкам', 'films_by_rating')],
            [Generator.create_button('Поиск фильмов 🔎', 'search_my_films')],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)

    @staticmethod
    def create_all_my_films_kb(
            films: dict[int, str]) -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button(
                title,
                f'my_film-{film_id}') for film_id, title in films.items()
             ],
            Buttons.create_navigation_buttons()
        ]

        return Generator.create_keyboard(buttons, 2)

    @staticmethod
    def create_film_info_kb() -> InlineKeyboardMarkup:
        buttons = [
            [Generator.create_button('Оценка', 'my_film_rating'),
             Generator.create_button('Рецензия', 'my_film_review')],
            [Generator.create_button('Страница в Википедии',
                                     'my_film_wiki_link')],
            Buttons.create_navigation_buttons()
        ]
        return Generator.create_keyboard(buttons, 2)
