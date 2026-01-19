from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def start_registration_keyboard():
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки по одной
    builder.add(types.InlineKeyboardButton(
        text="Начать регистрацию",
        callback_data="start_registration"
    ))

    return builder.as_markup()

def return_keyboard():
    """Создает клавиатуру с кнопками Вернуться в основное меню"""

    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text="Вернуться в основное меню")
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)