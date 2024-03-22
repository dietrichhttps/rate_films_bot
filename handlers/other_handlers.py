import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.state import default_state

router = Router()

logger = logging.getLogger(__name__)


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    logger.debug('Inside send_echo')
    await message.reply(text='Извините, моя твоя не понимать')
