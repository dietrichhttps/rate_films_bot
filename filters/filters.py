import re

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsRate(BaseFilter):
    async def __call__(self, message: Message):
        rate = message.text.strip()
        return re.match(r'^(?:[0-9]|10)$', rate) and rate.isdigit()
