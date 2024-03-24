from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_ratings_keyboard() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for rating in reversed(range(11)):
        kb_builder.row(InlineKeyboardButton(
            text=str(rating),
            callback_data=f'rating-{rating}'
        ))

    return kb_builder.as_markup()
