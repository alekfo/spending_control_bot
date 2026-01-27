from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def employees_main_menu_keyboard():
    """Создает инлайн-клавиатуру с двумя кнопками в столбик"""

    builder = InlineKeyboardBuilder()

    # Добавляем кнопки по одной
    builder.row(types.InlineKeyboardButton(
        text="💰Показать мои расходы",
        callback_data="show_my_spendings"
    ))
    builder.row(types.InlineKeyboardButton(
        text="➕Добавить расход",
        callback_data="add_spending"
    ))

    return builder.as_markup()

def job_title_keyboard():
    """Создаем клавиатуру с должностями"""

    builder = InlineKeyboardBuilder()

    # Описываем все кнопки
    builder.add(
        types.InlineKeyboardButton(
            text="🚚Водитель",
            callback_data="driver"
        ),
        types.InlineKeyboardButton(
            text="📊Логист",
            callback_data="logistician"
        ),
        types.InlineKeyboardButton(
            text="💪Грузчик",
            callback_data="loader"
        ),
        types.InlineKeyboardButton(
            text="↩️Назад",
            callback_data="back"
        )

    )

    # Указываем, как расположить кнопки: 1 в первом ряду
    builder.adjust(1)

    return builder.as_markup()

def confirmation_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=f"approve_registration_{user_id}"
        ),
        types.InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"reject_registration_{user_id}"
        )
    )

    return builder.as_markup()