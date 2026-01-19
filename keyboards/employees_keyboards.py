from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def employees_main_menu_keyboard():
    """Создает инлайн-клавиатуру с двумя кнопками в столбик"""

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки по одной
    builder.add(types.InlineKeyboardButton(
        text="Показать мои расходы",
        callback_data="show_my_spendings"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Добавить расход",
        callback_data="show_spending"
    ))

    return builder.as_markup()