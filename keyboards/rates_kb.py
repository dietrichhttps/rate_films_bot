from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_rates_keyboard() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for rate in reversed(range(11)):
        kb_builder.row(InlineKeyboardButton(
            text=str(rate),
            callback_data=f'rate-{rate}'
        ))

    return kb_builder.as_markup()
