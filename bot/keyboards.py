from aiogram import types

kick_button = types.InlineKeyboardButton('Kick', callback_data='kick')
leave_button = types.InlineKeyboardButton('No kick', callback_data='leave')
kick_keyboard = types.InlineKeyboardMarkup().row(kick_button, leave_button)
