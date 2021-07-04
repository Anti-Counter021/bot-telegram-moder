from aiogram import Bot, Dispatcher, types, executor

import logging

from config import TOKEN, GROUP_ID
from filters import IsAdminFilter
from sqlighter import SQLighter

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode='HTML')
dispatcher = Dispatcher(bot)
dispatcher.filters_factory.bind(IsAdminFilter)
db = SQLighter('members.db')


# New warning
@dispatcher.message_handler(commands=['warning'], is_admin=True)
async def add_new_warning(message: types.Message):

    if not message.reply_to_message:
        await message.reply('Command need use with reply message!')
        return

    user_may_be_is_admin = await message.bot.get_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
    if user_may_be_is_admin.is_chat_admin():
        await message.reply('Error give warning admin!')
        return

    user = message.reply_to_message.from_user
    user_id = user.id
    db.add_new_warning(user_id)
    count_warning = db.get_count_warnings(user_id)
    await message.bot.delete_message(GROUP_ID, message.message_id)

    if count_warning >= 3:
        await bot.send_message(GROUP_ID, f'We warned you! @{user.username}')
        await message.bot.kick_chat_member(GROUP_ID, user_id, revoke_messages=True)
        await bot.send_message(GROUP_ID, f'User @{user.username} has been banned!')
        await message.bot.send_photo(message.chat.id, 'https://airsofter.world/galleries/3857/5cb720e8783a1.jpg')
    else:
        await bot.send_message(
            GROUP_ID, f'You have {count_warning} warnings! If you have 3 warnings we ban you! @{user.username}',
        )


# New add link
@dispatcher.message_handler(commands=['link'])
async def get_add_link(message: types.Message):
    link = await message.bot.create_chat_invite_link(message.chat.id)
    await message.answer(link['invite_link'])


# Ban
@dispatcher.message_handler(is_admin=True, commands=['ban'])
async def ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply('Command need use with reply message!')
        return

    user = await message.bot.get_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
    if user.is_chat_admin():
        await message.reply('Error ban admin!')
        return

    await message.bot.delete_message(GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(GROUP_ID, message.reply_to_message.from_user.id, revoke_messages=True)

    await message.reply_to_message.reply(f'User @{message.reply_to_message.from_user.username} has been banned!')
    await message.bot.send_photo(message.chat.id, 'https://airsofter.world/galleries/3857/5cb720e8783a1.jpg')


# Delete service messages
@dispatcher.message_handler(
    content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo']
)
async def on_user_joined(message: types.Message):
    if message.content_type == 'new_chat_members':
        for member in message.new_chat_members:
            db.add_user(member['id'])
            db.add_new_warning(member['id'], 0)
    await message.delete()


# Delete messages with types ['url', 'text_link', 'email', 'phone_number']
@dispatcher.message_handler()
async def filter_message_with_link(message: types.Message):
    for entity in message.entities:
        if entity.type in ['url', 'text_link', 'email', 'phone_number']:
            await message.delete()


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
