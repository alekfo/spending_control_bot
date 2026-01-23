from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

# Создаем клавиатуру для приветствия
def admins_main_menu_keyboard():
    """
    Создает инлайн-клавиатуру с двумя кнопками в столбик
    """
    builder = InlineKeyboardBuilder()

    admin_menu_sections = [
        ("👤👤Все сотрудники", "get_all_employees"),
        ("💰Расходы сотрудника", "spendings"),
        ("Синхронизировать Google-таблицу", "synchronize")
    ]

    for i_section in admin_menu_sections:
        # Добавляем кнопки по одной
        builder.row(types.InlineKeyboardButton(
            text=i_section[0],
            callback_data=i_section[1]
        ))

    builder.row(types.InlineKeyboardButton(
        text="🔗Ссылка на таблицу",
        url="https://docs.google.com/spreadsheets/d/1Q3LadqbbZx3MVwuOVo9I76iPfQkxW-Ah9jbe_bAvWAo/edit?gid=0#gid=0"))

    return builder.as_markup()