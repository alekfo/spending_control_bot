from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

# Создаем клавиатуру для приветствия
def admins_main_menu_keyboard():
    """
    Создает инлайн-клавиатуру с двумя кнопками в столбик
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки по одной
    builder.row(types.InlineKeyboardButton(
        text="Все сотрудники",
        callback_data="get_all_employees"
    ))
    builder.row(types.InlineKeyboardButton(
        text="Расходы сотрудника",
        callback_data="spendings"
    ))
    builder.row(types.InlineKeyboardButton(
            text="Ссылка на таблицу",
            url="https://docs.google.com/spreadsheets/d/1Q3LadqbbZx3MVwuOVo9I76iPfQkxW-Ah9jbe_bAvWAo/edit?gid=0#gid=0"))

    return builder.as_markup()