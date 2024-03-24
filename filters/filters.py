import re

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsRating(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        rating = callback.data.split('rating-')[1].strip()
        return re.match(r'^(?:[0-9]|10)$', rating) and rating.isdigit()
