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
