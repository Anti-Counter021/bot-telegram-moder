from aiogram import Bot, Dispatcher, types, executor

import logging

from config import TOKEN, GROUP_ID
from filters import IsAdminFilter
from keyboards import kick_keyboard
from sql.sqlighter import UserTable, VoteTable

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode='HTML')
dispatcher = Dispatcher(bot)
dispatcher.filters_factory.bind(IsAdminFilter)
db_user = UserTable('members.db')
db_vote = VoteTable('members.db')

KICK_MESSAGE_ID: int = 0


# cancel vote kick !!!
# rules, help, chat_id


# Vote for kick
@dispatcher.message_handler(commands=['kick'])
async def vote_for_kick(message: types.Message):
    global KICK_MESSAGE_ID

    if KICK_MESSAGE_ID:
        await message.reply('There is already a valid vote for the kick!')
        return

    if not message.reply_to_message:
        await message.reply('Command need use with reply message!')
        return

    user_may_be_is_admin = await message.bot.get_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
    if user_may_be_is_admin.is_chat_admin():
        await message.reply('Error give warning admin!')
        return

    await message.reply(
        f'New vote for kick @{message.reply_to_message.from_user.username}, organized @{message.from_user.username}',
        reply_markup=kick_keyboard,
    )
    KICK_MESSAGE_ID = message.message_id
    kick_id = message.reply_to_message.from_user.id
    user_id = message.from_user.id
    if not db_user.exists(kick_id):
        db_user.add_user(kick_id)
    if not db_user.exists(user_id):
        db_user.add_user(user_id)
    kick = db_user.get_id(kick_id)
    user = db_user.get_id(user_id)
    db_vote.create_new_vote(user_id=user, message_id=KICK_MESSAGE_ID, kick_id=kick)


@dispatcher.callback_query_handler(lambda callback_data: callback_data.data)
async def callback(callback_query: types.CallbackQuery):
    global KICK_MESSAGE_ID

    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == 'kick':
        user_id = callback_query.from_user.id
        if not db_user.exists(user_id):
            db_user.add_user(user_id)
        user = db_user.get_id(user_id)
        if not db_vote.exists(user, KICK_MESSAGE_ID):
            db_vote.create_votes_user(user_id=user, message_id=KICK_MESSAGE_ID)
        count_votes = db_vote.count_votes_for_kick(KICK_MESSAGE_ID)
        await bot.send_message(GROUP_ID, f'Votes for kick {count_votes}')

        if count_votes >= 1:
            await bot.edit_message_reply_markup(
                callback_query.message.chat.id, callback_query.message.message_id, reply_markup=None,
            )
            kick = db_vote.get_kick_user_id(KICK_MESSAGE_ID)
            await bot.kick_chat_member(GROUP_ID, kick, revoke_messages=True)
            await bot.send_photo(GROUP_ID, 'https://airsofter.world/galleries/3857/5cb720e8783a1.jpg')
            KICK_MESSAGE_ID = 0


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
    db_user.add_new_warning(user_id)
    count_warning = db_user.get_count_warnings(user_id)
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
            db_user.add_user(member['id'])
            db_user.add_new_warning(member['id'], 0)
    await message.delete()


# Delete messages with types ['url', 'text_link', 'email', 'phone_number']
@dispatcher.message_handler()
async def filter_message_with_link(message: types.Message):
    for entity in message.entities:
        if entity.type in ['url', 'text_link', 'email', 'phone_number']:
            await message.delete()


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
