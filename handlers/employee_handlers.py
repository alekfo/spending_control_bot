from datetime import datetime
from io import BytesIO
import logging

from aiogram import types, F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, BufferedInputFile
from aiogram.types import ReplyKeyboardRemove

from config import admin_id
from keyboards.main_keyboards import return_keyboard, back_keyboard, month_keyboard
from keyboards.employees_keyboards import employees_main_menu_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler
from data.database import create_spending, get_spendings_by_month


logger = logging.getLogger(__name__)
employee_router = Router()


@employee_router.callback_query(lambda c: c.data == "add_spending", EmployeeStates.in_employees_main_menu)
async def start_add_spending(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Добавить расход"
    только в состоянии EmployeeStates.in_employees_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(EmployeeStates.getting_amount_off_spending)

    # Отправляем новое сообщение
    await callback_query.message.answer(
        "💳Сколько потратили?\n\n"
        "Введите количество в рублях",
        parse_mode="Markdown",
        reply_markup=return_keyboard()
    )

@employee_router.message(StateFilter(EmployeeStates.getting_amount_off_spending))
async def got_amount_of_spending(message: types.Message, state: FSMContext):

    try:
        amount_of_spending = message.text.strip()
        if not amount_of_spending.isdigit():
            raise ValueError(
                'Некорретный ввод. Сумма должна состоять только из цифр. Попробуйте ввести снова')
    except ValueError as e:
        await message.answer(
            f"❌Ошибка! {e}",
            reply_markup=return_keyboard()
        )
    else:
        # Сохраняем данные пользователя в state
        await state.update_data(
            amount_of_spending=amount_of_spending
        )

        await state.set_state(EmployeeStates.getting_purpose_off_spending)

        # Отправляем новое сообщение
        await message.answer(
            "🎯Какова цель траты?",
            parse_mode="Markdown",
            reply_markup=return_keyboard()
        )


@employee_router.message(StateFilter(EmployeeStates.getting_purpose_off_spending))
async def got_purpose_of_spending(message: types.Message, state: FSMContext):
    purpose_of_spending = message.text.strip()

    # Сохраняем данные пользователя в state
    await state.update_data(
        purpose_of_spending=purpose_of_spending
    )

    await state.set_state(EmployeeStates.getting_details_off_spending)

    # Отправляем новое сообщение
    await message.answer(
        "📝Напишите детали.\n\n"
        "Или просто отправьте НЕТ",
        parse_mode="Markdown",
        reply_markup=return_keyboard()
    )

@employee_router.message(StateFilter(EmployeeStates.getting_details_off_spending))
async def end_adding_spending(message: types.Message, state: FSMContext):
    details = message.text.strip()
    employees_id = message.from_user.id

    spending_data = await state.get_data()
    spending = spending_data.get('amount_of_spending', '')
    purpose = spending_data.get('purpose_of_spending', '')

    try:
        result = await create_spending(
            employees_id, spending, details, purpose
        )
        logger.info(f"Добавлена новая трата: ID сотрудника: {employees_id}, Сумма: {spending}")

    except Exception as e:
        logger.error(f"Ошибка добавления расхода: {e}")
        await message.answer(
            f"❌ Ошибка добавления расхода в базу: {e}",
            reply_markup=return_keyboard()
        )
    else:
        if result:
            await state.set_state(EmployeeStates.in_employees_main_menu)
            await message.answer(
                f"✅Расход успешно добавлен в базу",
                reply_markup=return_keyboard()
            )

@employee_router.callback_query(lambda c: c.data == "show_my_spendings", EmployeeStates.in_employees_main_menu)
async def start_add_spending(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Показать мои расходы"
    только в состоянии EmployeeStates.in_employees_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(EmployeeStates.getting_month_to_show_spendings)

    # Отправляем новое сообщение
    await callback_query.message.answer(
        "📅 За какой месяц хотите посмотреть?",
        parse_mode="Markdown",
        reply_markup=month_keyboard()
    )

@employee_router.callback_query(EmployeeStates.getting_month_to_show_spendings)
async def got_month_to_show_spending(callback_query: types.CallbackQuery, state: FSMContext):


    month_list = [
        'January', 'February', 'March',
        'April', 'May', 'June', 'July',
        'August', 'September', 'October',
        'November', 'December'
    ]
    month_to_check = callback_query.data
    employee_id = callback_query.from_user.id

    if month_to_check not in month_list:
        if month_to_check == "back":
            # Удаляем сообщение с должностями
            await callback_query.message.delete()
            await state.set_state(EmployeeStates.in_employees_main_menu)
            await callback_query.message.answer(
                '💼 Выберите действие в системе:',
                parse_mode="Markdown",
                reply_markup=employees_main_menu_keyboard()
            )
            return

        await callback_query.message.answer(
            "🔙❌ Пожалуйста, выберите месяц из предложенных вариантов",
            parse_mode="Markdown",
            reply_markup=month_keyboard()
        )
        return

    await callback_query.answer(f"Загрузка расходов за {month_to_check}...")

    # Получаем номер месяца (1-12)
    month_number = month_list.index(month_to_check) + 1

    # Получаем расходы за месяц
    spendings = get_spendings_by_month(employee_id, month_number)

    if not spendings:
        logger.info(f"✅ Нет расходов для сотрудника {employee_id} за {month_to_check}")
        await callback_query.message.answer(
            f"📭 *Расходы за {month_to_check}*\n\n"
            f"У вас нет зарегистрированных расходов за этот месяц.",
            parse_mode="Markdown",
            reply_markup=return_keyboard()
        )
        await state.set_state(EmployeeStates.in_employees_main_menu)
        return

    # Форматируем вывод
    total_amount = 0
    output = f"📊 *ВАШИ РАСХОДЫ ЗА {month_to_check.upper()}*\n\n"

    for i, spending in enumerate(spendings, 1):
        amount = float(spending.spending) if spending.spending else 0
        total_amount += amount

        # Форматируем дату
        date_str = spending.date_of_spending.strftime("%d.%m.%Y %H:%M") if spending.date_of_spending else "Не указано"

        # Добавляем детали и цель
        details = f"\n   📝 *Детали:* {spending.details}" if spending.details else ""
        purpose = f"\n   🎯 *Цель:* {spending.purpose}" if spending.purpose else ""

        output += (
            f"{i}. 💰 *{amount:.2f} руб.*\n"
            f"   📅 *Дата:* {date_str}{details}{purpose}\n\n"
        )

    # Добавляем итоговую сумму
    output += f"💵 *ОБЩАЯ СУММА РАСХОДОВ:* {total_amount:.2f} руб.\n"
    output += f"📈 *Всего операций:* {len(spendings)}"

    logger.info(f"✅ Успешно сформированы траты сотрудника {employee_id} за {month_to_check}")

    # Отправляем результат
    await callback_query.message.answer(
        output,
        parse_mode="Markdown",
        reply_markup=return_keyboard()
    )

    # Возвращаем в главное меню
    await state.set_state(EmployeeStates.in_employees_main_menu)