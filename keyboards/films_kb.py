from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_suggestions_keyboard(
        suggestions: dict[str, str]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for title, link in suggestions.items():
        kb_builder.row(InlineKeyboardButton(
            text=title,
            callback_data=f'suggestion-{title}'
        ))
        kb_builder.row(InlineKeyboardButton(
            text='Ссылка на фильм',
            url=link
        ))
    return kb_builder.as_markup()


def create_my_films_keyboard() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    all_films_btn = InlineKeyboardButton(
        text='Все фильмы',
        callback_data='all_films'
    )
    films_by_rating_btn = InlineKeyboardButton(
        text='Фильмы по оценкам',
        callback_data='films_by_rating'
    )
    search_my_films_btn = InlineKeyboardButton(
        text='Поиск фильмов 🔎',
        callback_data='search_my_films'
    )
    kb_builder.row(
        all_films_btn, films_by_rating_btn,
        width=2
    )
    kb_builder.row(search_my_films_btn)
    return kb_builder.as_markup()


def create_all_my_films_keyboard(
        films: dict[int, str]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for film_id, title in films.items():
        kb_builder.row(InlineKeyboardButton(
            text=title,
            callback_data=f'my_film-{film_id}'
        ))
    return kb_builder.as_markup()


def create_film_info_keyboard() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    rating_btn = InlineKeyboardButton(
        text='Оценка',
        callback_data='my_film_rating'
    )
    review_btn = InlineKeyboardButton(
        text='Рецензия',
        callback_data='my_film_review'
    )
    wiki_link_btn = InlineKeyboardButton(
        text='Страница в Википедии',
        callback_data='my_film_rating'
    )
    kb_builder.row(rating_btn, review_btn, width=2)
    kb_builder.row(wiki_link_btn)
    return kb_builder.as_markup()
