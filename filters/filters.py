import re

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsRate(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        rate = callback.data.split('rate-')[1].strip()
        return re.match(r'^(?:[0-9]|10)$', rate) and rate.isdigit()
