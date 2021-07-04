from aiogram import Bot, Dispatcher, types, executor

import logging

from config import TOKEN, GROUP_ID
from filters import IsAdminFilter

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode='HTML')
dispatcher = Dispatcher(bot)
dispatcher.filters_factory.bind(IsAdminFilter)


# Ban
@dispatcher.message_handler(is_admin=True, commands=['ban'])
async def ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply('Command need use with reply message!')
        return

    user = await message.bot.get_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
    if user.is_chat_admin():
        await message.reply('Error ban admin')
        return

    await message.bot.delete_message(GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(GROUP_ID, message.reply_to_message.from_user.id, revoke_messages=True)

    await message.reply_to_message.reply('User has been banned!')
    await message.bot.send_photo(message.chat.id, 'https://airsofter.world/galleries/3857/5cb720e8783a1.jpg')


# Delete service messages
@dispatcher.message_handler(
    content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo']
)
async def on_user_joined(message: types.Message):
    await message.delete()


# Delete messages with types ['url', 'text_link', 'email', 'phone_number']
@dispatcher.message_handler()
async def filter_message_with_link(message: types.Message):
    for entity in message.entities:
        if entity.type in ['url', 'text_link', 'email', 'phone_number']:
            await message.delete()


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
