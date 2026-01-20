from math import lgamma

from config import admin_id
from keyboards.main_keyboards import return_keyboard, month_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler
from google_sheet_service.google_sheet_main import get_all_employees, does_employee_exists, get_spending_by_name

from datetime import datetime
from io import BytesIO
import logging
from aiogram import types, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, BufferedInputFile

from aiogram.types import ReplyKeyboardRemove

logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.callback_query(lambda c: c.data == "get_all_employees", AdminStates.in_admins_main_menu)
async def get_all_empoyees(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Все сотрудники"
    только в состоянии AdminStates.in_admins_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(AdminStates.getting_all_employees)

    result = get_all_employees()

    # Отправляем новое сообщение
    await callback_query.message.answer(
        f"Все сотрудники:\n{result}",
        reply_markup=return_keyboard()
    )

@admin_router.callback_query(lambda c: c.data == "spendings", AdminStates.in_admins_main_menu)
async def get_employees_id_to_get_spending(callback_query: types.CallbackQuery, state: FSMContext):
    """"
    Обработчик callback-запроса от кнопки "Расходы сотрудника"
    только в состоянии AdminStates.in_admins_main_menu
    """
    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(AdminStates.getting_employees_id_to_get_spending)

    await callback_query.message.answer(
        f"Введите ID сотрудника",
        reply_markup=return_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.getting_employees_id_to_get_spending))
async def get_month_to_get_spending(message: types.Message, state: FSMContext):
    employees_id = message.text
    if not does_employee_exists(employees_id):
        await message.answer(
            f"Введите корреткный ID сотрудника",
            reply_markup=return_keyboard()
        )
        return

    # Сохраняем данные сотрудника в state
    await state.update_data(
        employees_id=employees_id
    )

    await state.set_state(AdminStates.getting_month_to_get_spending)
    await message.answer(
        f"За какой месяц получить расходы?",
        reply_markup=month_keyboard()
    )

@admin_router.callback_query(StateFilter(AdminStates.getting_month_to_get_spending))
async def get_spending(callback_query: types.CallbackQuery, state: FSMContext):
    month_list = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
    ]
    month_to_check = callback_query.data
    if month_to_check not in month_list:
        if month_to_check == "back":
            # Удаляем сообщение с месяцами
            await callback_query.message.delete()
            await state.set_state(AdminStates.getting_employees_id_to_get_spending)
            await callback_query.message.answer(
                f"Введите ID сотрудника",
                reply_markup=return_keyboard()
            )
            return
        await callback_query.message.answer(
            f"Выберите месяц из педложенных",
            reply_markup=month_keyboard()
        )
        return

    await state.update_data(
        month_to_check=month_to_check
    )

    await state.set_state(AdminStates.getting_employee_spending)

    employee_data = await state.get_data()

    clients_id = employee_data.get('employees_id', '')

    res = get_spending_by_name(clients_id, month_to_check)

    await callback_query.message.answer(
        f"Расходы {clients_id} за {month_to_check}:\n{res}",
        reply_markup=return_keyboard()
    )