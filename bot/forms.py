from aiogram.dispatcher.filters.state import StatesGroup, State


class Captcha(StatesGroup):
    """ Captcha """

    captcha = State()
    user_id = State()
    x = State()
    y = State()
