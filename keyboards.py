from aiogram import types

kick_button = types.InlineKeyboardButton('Kick', callback_data='kick')
kick_keyboard = types.InlineKeyboardMarkup().row(kick_button)
