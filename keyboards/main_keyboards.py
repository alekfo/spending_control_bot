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
        types.KeyboardButton(text="↩️Вернуться в основное меню")
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def back_keyboard():
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки по одной
    builder.add(types.InlineKeyboardButton(
        text="↩️Назад",
        callback_data="back"
    ))

    return builder.as_markup()

def month_keyboard():
    """Создаем клавиатуру с месяцами"""

    builder = InlineKeyboardBuilder()

    # Описываем все кнопки
    builder.add(
        types.InlineKeyboardButton(
            text="Январь",
            callback_data="January"
        ),
        types.InlineKeyboardButton(
            text="Февраль",
            callback_data="February"
        ),
        types.InlineKeyboardButton(
            text="Март",
            callback_data="March"
        ),
        types.InlineKeyboardButton(
            text="Апрель",
            callback_data="April"
        ),
        types.InlineKeyboardButton(
            text="Май",
            callback_data="May"
        ),
        types.InlineKeyboardButton(
            text="Июнь",
            callback_data="June"
        ),
        types.InlineKeyboardButton(
            text="Июль",
            callback_data="July"
        ),
        types.InlineKeyboardButton(
            text="Август",
            callback_data="August"
        ),
        types.InlineKeyboardButton(
            text="Сентябрь",
            callback_data="September"
        ),
        types.InlineKeyboardButton(
            text="Октябрь",
            callback_data="October"
        ),
        types.InlineKeyboardButton(
            text="Ноябрь",
            callback_data="November"
        ),
        types.InlineKeyboardButton(
            text="Декабрь",
            callback_data="December"
        ),
        types.InlineKeyboardButton(
            text="Назад",
            callback_data="back"
        )

    )

    # Указываем, как расположить кнопки: 2 в первом ряду
    builder.adjust(2, 2, 2, 2, 2, 2, 1)

    return builder.as_markup()