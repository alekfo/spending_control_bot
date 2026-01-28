from math import lgamma
from datetime import datetime
from io import BytesIO
import logging

from aiogram import types, F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, BufferedInputFile
from aiogram.types import ReplyKeyboardRemove

from config import admin_id
from keyboards.main_keyboards import return_keyboard, month_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler
from google_sheet_service.google_sheet_main import synchronize
from data.database import get_all_employees, does_employee_exists, get_spendings_by_month, add_new_employee, get_session
from handlers.registration_handlers import pending_registrations




logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.callback_query(lambda c: c.data == "synchronize", AdminStates.in_admins_main_menu)
async def synchronize_google_sheet(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Синхронизировать Google-таблицу"
    только в состоянии AdminStates.in_admins_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    try:
        result = await synchronize()
    except Exception as e:
        logger.error(f"Ошибка при синхронизации Google-таблицы: {e}")
        await callback_query.message.answer(
            f"Ошибка при синхронизации Google-таблицы: {e}",
            reply_markup=return_keyboard()
        )
        return


    await callback_query.message.answer(
        f"✅Таблицы успешно синзронизированы",
        reply_markup=return_keyboard()
    )


@admin_router.callback_query(lambda c: c.data == "get_all_employees", AdminStates.in_admins_main_menu)
async def get_all_employees_hand(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Все сотрудники"
    только в состоянии AdminStates.in_admins_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()

    employees = await get_all_employees()

    if not employees:
        logger.info(f"✅ Список сотрудников пуст для получения")
        await callback_query.message.answer(
            "📭 *Список сотрудников пуст*\n\n"
            "В системе пока нет зарегистрированных сотрудников.",
            parse_mode="Markdown",
            reply_markup=return_keyboard()
        )
        return

    output = "👥 *СПИСОК СОТРУДНИКОВ*\n\n"

    for i, emp in enumerate(employees, 1):
        # Определяем эмодзи для должности
        job_emoji = {
            'driver': '🚚',
            'logistician': '📊',
            'loader': '💪'
        }.get(emp.job_title, '👤')

        output += (
            f"{i}. {job_emoji} *{emp.name}*\n"
            f"   ├─ 🆔 TG ID: `{emp.clients_telegram_id}`\n"
            f"   ├─ 💼 Должность: {emp.job_title}\n"
            f"   └─ 🔢 Таб. номер: {emp.employees_work_number}\n\n"
        )
    output += f"📊 *Всего сотрудников:* {len(employees)}"

    logger.info(f"✅ Успешно получен список сотрудников")

    await callback_query.message.answer(
        output,
        parse_mode="Markdown",
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
        f"✏️Введите телеграм-ID сотрудника",
        reply_markup=return_keyboard()
    )

@admin_router.message(StateFilter(AdminStates.getting_employees_id_to_get_spending))
async def get_month_to_get_spending(message: types.Message, state: FSMContext):

    try:
        employees_id = int(message.text)
    except ValueError as e:
        await message.answer(
            f"⚠️Телеграм-ID сотрудника может состоять только из цифр. Попробуйте снова",
            reply_markup=return_keyboard()
        )
        return
    if not does_employee_exists(employees_id):
        await message.answer(
            f"⚠️️Сотрудника с таким телеграм-ID не существует. Попробуйте снова",
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
                f"✏️Введите телеграм-ID сотрудника",
                reply_markup=return_keyboard()
            )
            return
        await callback_query.message.answer(
            f"⚠️Выберите месяц из педложенных",
            reply_markup=month_keyboard()
        )
        return

    await state.update_data(
        month_to_check=month_to_check
    )

    month_number = month_list.index(month_to_check) + 1

    employee_data = await state.get_data()

    clients_id = employee_data.get('employees_id', '')

    spendings = get_spendings_by_month(clients_id, month_number)

    if not spendings:
        logger.info(f"✅ У сотрудника {clients_id} не расходов за {month_to_check}")
        await callback_query.message.answer(
            f"📭 *Расходы за {month_to_check}*\n\n"
            f"У сотрудника нет расходов за указанный месяц.",
            parse_mode="Markdown",
            reply_markup=return_keyboard()
        )
        await state.set_state(AdminStates.in_admins_main_menu)
        return

    # Форматируем вывод
    total_amount = 0
    output = f"📊 *Расходы сотрудника с ID {clients_id} за {month_to_check.upper()}*\n\n"

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

    logger.info(f"✅ Успешно получен список рассходов сотрудника {clients_id} за {month_to_check}")
    # Отправляем результат
    await callback_query.message.answer(
        output,
        parse_mode="Markdown",
        reply_markup=return_keyboard()
    )

# Обработчик для админских действий
@admin_router.callback_query(lambda c: c.data.startswith(("approve_registration_", "reject_registration_")))
async def handle_registration_decision(callback_query: types.CallbackQuery, bot: Bot):
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
    user_state = pending_registrations[user_id]['state']

    if action == 'approve':
        # Добавляем пользователя в Google Sheets
        session = get_session()
        try:
            result = await add_new_employee(
                user_id,
                user_data.get('employees_name', ''),
                user_data.get('job_title', ''),
                user_data.get('employees_work_number', '')
            )
            logger.info(f"Добавлен новый пользователь: Имя: {user_data.get('employees_name', '')}, Телеграм-id: {user_id}")

            if result:
                await user_state.clear()
                await user_state.set_state(EmployeeStates.in_employees_main_menu)

                # Отправляем уведомление пользователю
                await bot.send_message(
                    chat_id=user_id,
                    text="✅ *Ваша регистрация подтверждена администратором!*\n\n"
                         f"Добро пожаловать в систему, {user_data.get('employees_name', '')}!\n\n"
                         f"Чтобы начать - жми /start",
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
        await user_state.clear()
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