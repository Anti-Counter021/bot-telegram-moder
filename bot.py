from aiogram import Bot, Dispatcher, types, executor

import logging

from config import TOKEN


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler()
async def filter_message_with_link(message: types.Message):
    if 'http' in message.text:
        await message.delete()


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
