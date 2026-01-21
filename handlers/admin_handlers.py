from math import lgamma

from config import admin_id
from keyboards.main_keyboards import return_keyboard, month_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler
from google_sheet_service.google_sheet_main import get_all_employees, does_employee_exists, get_spending_by_name, add_new_employee
from employees_handlers import pending_registrations

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
async def get_all_employees_hand(callback_query: types.CallbackQuery, state: FSMContext):
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

# Обработчик для админских действий
@admin_router.callback_query(lambda c: c.data.startswith(("approve_registration_", "reject_registration_")))
async def handle_registration_decision(callback_query: types.CallbackQuery, bot: types.Bot):
    """Обработка решения админа по регистрации"""
    await callback_query.answer()

    parts = callback_query.data.split('_')
    action = parts[0]  # "approve" или "reject"
    user_id_str = parts[2]  # "123456"

    user_id = int(user_id_str)

    if user_id not in pending_registrations:
        await callback_query.message.edit_text(
            "⚠️ Данные пользователя уже обработаны или устарели.",
            reply_markup=None
        )
        return

    user_data = pending_registrations[user_id]['data']

    if action == 'approve':
        # Добавляем пользователя в Google Sheets
        try:
            result = add_new_employee(
                user_id=str(user_id),
                full_name=user_data.get('employees_name', ''),
                job_title=user_data.get('job_title', ''),
                work_number=user_data.get('employees_work_number', '')
            )

            if result:
                # Отправляем уведомление пользователю
                await bot.send_message(
                    chat_id=user_id,
                    text="✅ *Ваша регистрация подтверждена администратором!*\n\n"
                         f"Добро пожаловать в систему, {user_data.get('employees_name', '')}!",
                    parse_mode="Markdown"
                )

                # Обновляем сообщение админу
                await callback_query.message.edit_text(
                    f"✅ Регистрация пользователя {user_data.get('employees_name', '')} подтверждена и добавлена в систему.",
                    reply_markup=None
                )
            else:
                raise Exception("Ошибка добавления в таблицу")

        except Exception as e:
            logger.error(f"Ошибка добавления пользователя в таблицу: {e}")
            await callback_query.message.edit_text(
                f"❌ Ошибка при добавлении пользователя в систему: {e}",
                reply_markup=None
            )

    else:  # reject_registration
        # Отправляем уведомление пользователю об отказе
        await bot.send_message(
            chat_id=user_id,
            text="❌ *Ваша регистрация отклонена администратором.*\n\n"
                 "Пожалуйста, свяжитесь с администратором для уточнения деталей.",
            parse_mode="Markdown"
        )

        # Обновляем сообщение админу
        await callback_query.message.edit_text(
            f"❌ Регистрация пользователя {user_data.get('employees_name', '')} отклонена.",
            reply_markup=None
        )

        # Удаляем пользователя из списка ожидающих
    del pending_registrations[user_id]