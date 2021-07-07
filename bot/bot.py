from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import logging

from random import randint

from config import TOKEN, GROUP_ID
from filters import IsAdminFilter
from forms import Captcha
from keyboards import kick_keyboard
from sql.sqlighter import UserTable, VoteTable

assert GROUP_ID, 'No GROUP_ID'
assert TOKEN, 'NO TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
dispatcher.filters_factory.bind(IsAdminFilter)
db_user = UserTable('members.db')
db_vote = VoteTable('members.db')

KICK_MESSAGE_ID: int = 0


@dispatcher.message_handler(commands=['captcha'])
async def captcha(message: types.Message, state: FSMContext):
    x = randint(1, 9)
    y = randint(1, 9)
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
        data['x'] = x
        data['y'] = y
    await message.reply(f'Please input {x} + {y}. @{message.from_user.username}')
    await Captcha.captcha.set()


@dispatcher.message_handler(state=Captcha.captcha)
async def process_captcha(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        x = data['x']
        y = data['y']
        try:
            data['captcha'] = int(message.text)
            assert data['user_id'] == message.from_user.id, 'User.id != message.from_user.id'
        except ValueError:
            data['captcha'] = ''
        finally:
            if x + y != data['captcha']:
                await bot.kick_chat_member(message.chat.id, message.from_user.id, revoke_messages=True)
            else:
                await message.answer('Good!')
    await state.finish()


@dispatcher.message_handler(commands=['help'])
async def help_bot(message: types.Message):
    """ Help """
    await message.answer(
        'My commands:\n'
        '\t\t\t\t<strong>/info</strong> - Information about me\n'
        '\t\t\t\t<strong>/link</strong> - Invite link\n'
        '\t\t\t\t<strong>/kick</strong> - Vote for kick. Need reply message\n'
        '\t\t\t\t<strong>/chat</strong> - Id chat - only admin\n'
        '\t\t\t\t<strong>/warning</strong> - Need reply message. Warning - only admin\n'
        '\t\t\t\t<strong>/ban</strong> - Need reply message. Ban - only admin'
    )


@dispatcher.message_handler(commands=['info'])
async def info(message: types.Message):
    """ Information about bot """
    await message.answer('I\'m <strong>Bot Moderator by _Counter021_!</strong>\nInput /help for detail information')


@dispatcher.message_handler(commands=['chat'], is_admin=True)
async def get_chat_id(message: types.Message):
    """ Get chat ID """
    assert message.chat.id != GROUP_ID, 'GROUP_ID != chat.id'
    await message.answer(f'Chat id = {message.chat.id}')


@dispatcher.message_handler(commands=['kick'])
async def vote_for_kick(message: types.Message):
    """ Vote for kick """
    global KICK_MESSAGE_ID

    if KICK_MESSAGE_ID:
        await message.reply('There is already a valid vote for the kick!')
        return

    if not message.reply_to_message:
        await message.reply('Command need use with reply message!')
        return

    user_may_be_is_admin = await message.bot.get_chat_member(GROUP_ID, message.reply_to_message.from_user.id)
    if user_may_be_is_admin.is_chat_admin():
        await message.reply('Error kick admin!')
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

    assert db_user.exists(kick_id), 'Kick_id is not exists'
    assert db_user.exists(user_id), 'User_id is not exists'

    kick = db_user.get_id(kick_id)
    user = db_user.get_id(user_id)

    assert kick, 'Kick not id'
    assert user, 'User not id'

    db_vote.create_new_vote(user_id=user, message_id=KICK_MESSAGE_ID, kick_id=kick)


@dispatcher.message_handler(commands=['warning'], is_admin=True)
async def add_new_warning(message: types.Message):
    """ New warning """

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


@dispatcher.message_handler(commands=['link'])
async def get_add_link(message: types.Message):
    """ New invite link """
    link = await message.bot.create_chat_invite_link(message.chat.id)
    await message.answer(link['invite_link'])


@dispatcher.message_handler(is_admin=True, commands=['ban'])
async def ban(message: types.Message):
    """ Ban """
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


@dispatcher.message_handler(
    content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo']
)
async def on_user_joined(message: types.Message):
    """ Delete service messages """
    if message.content_type == 'new_chat_members':
        for member in message.new_chat_members:
            db_user.add_user(member['id'])
            db_user.add_new_warning(member['id'], 0)
            assert db_user.get_count_warnings(member.id) == 0, 'Member warning not is 0'
    await message.delete()


@dispatcher.message_handler()
async def filter_message_with_link(message: types.Message):
    """ Delete messages with types ['url', 'text_link', 'email', 'phone_number'] """
    for entity in message.entities:
        if entity.type in ['url', 'text_link', 'email', 'phone_number']:
            await message.delete()


@dispatcher.callback_query_handler(lambda callback_data: callback_data.data)
async def callback(callback_query: types.CallbackQuery):
    """ Treatment callback data """
    global KICK_MESSAGE_ID

    await bot.answer_callback_query(callback_query.id)

    if callback_query.data in ('kick', 'leave'):
        user_id = callback_query.from_user.id

        if not db_user.exists(user_id):
            db_user.add_user(user_id)

        assert db_user.exists(user_id), 'User_id is not exists'

        user = db_user.get_id(user_id)

        assert user, 'User not id'

        if not db_vote.exists(user, KICK_MESSAGE_ID):
            if callback_query.data == 'kick':
                db_vote.create_votes_user(user_id=user, message_id=KICK_MESSAGE_ID)
            elif callback_query.data == 'leave':
                db_vote.create_votes_user(user_id=user, message_id=KICK_MESSAGE_ID, act=False)

        count_votes_kick = db_vote.count_votes_for_kick(KICK_MESSAGE_ID)
        count_votes_leave = db_vote.count_votes_for_kick(KICK_MESSAGE_ID, False)
        await bot.send_message(GROUP_ID, f'Votes for kick {count_votes_kick} and no kick is {count_votes_leave}')

        if count_votes_kick >= 2:
            await bot.edit_message_reply_markup(
                callback_query.message.chat.id, callback_query.message.message_id, reply_markup=None,
            )
            kick = db_vote.get_kick_user_id(KICK_MESSAGE_ID)
            await bot.kick_chat_member(GROUP_ID, kick, revoke_messages=True)
            await bot.send_photo(GROUP_ID, 'https://airsofter.world/galleries/3857/5cb720e8783a1.jpg')
            KICK_MESSAGE_ID = 0
        elif count_votes_leave >= 2:
            await bot.edit_message_reply_markup(
                callback_query.message.chat.id, callback_query.message.message_id, reply_markup=None,
            )
            await bot.send_message(GROUP_ID, 'You lucky man!')
            KICK_MESSAGE_ID = 0


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
