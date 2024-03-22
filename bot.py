import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from config_data.config import load_config, Config
from handlers import other_handlers, user_handlers  # , admin_handlers
# from database.orm import TableORM

sys.path.insert(1, os.path.join(sys.path[0], '..'))


# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Создаем таблицы
    # TableORM.create_tables()

    # Конфигурируем логгирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        parse_mode='HTML')
    dp = Dispatcher()

    # Регистрируем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    # dp.include_router(admin_handlers.router)
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
