from config import admin_id
from keyboards.main_keyboards import return_keyboard, back_keyboard
from keyboards.employees_keyboards import job_title_keyboard, confirmation_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler

from datetime import datetime
from io import BytesIO
import logging
from aiogram import types, F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, BufferedInputFile

from aiogram.types import ReplyKeyboardRemove

logger = logging.getLogger(__name__)
employee_router = Router()

# Словарь для хранения ожидающих подтверждения пользователей
pending_registrations = {}

@employee_router.callback_query(lambda c: c.data == "start_registration", EmployeeStates.wait_for_start)
async def start_registration(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Начать регистрацию"
    только в состоянии EmployeeStates.wait_for_start
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(EmployeeStates.getting_employees_name)


    # Отправляем новое сообщение
    await callback_query.message.answer(
        "👤 *Регистрация сотрудника*\n\n"
        "📝 Введите Ваше полное ФИО (Иванов Иван Иванович):",
        parse_mode="Markdown",
        reply_markup=return_keyboard()
    )

@employee_router.message(StateFilter(EmployeeStates.getting_employees_name))
async def start_registration(message: types.Message, state: FSMContext):
    try:

        employees_name = message.text
        employees_name_list = employees_name.split()
        if len(employees_name_list) != 3:
            raise ValueError('Некорретный ввод. ФИО должно быть полным. Попробуйте снова')
        if any([not i_part.isalpha() for i_part in employees_name_list]):
            raise ValueError('Некорретный ввод. ФИО не должно состоять из цифр. Попробуйте снова')
    except ValueError as e:
        await message.answer(
            f"❌Ошибка! {e}",
            reply_markup=return_keyboard()
        )
    else:
        await state.set_state(EmployeeStates.getting_employees_job_title)
        # Сохраняем данные пользователя в state
        await state.update_data(
            employees_name=employees_name
        )
        await message.answer(
            f"✅ *ФИО сохранено:* {employees_name}\n\n"
            f"💼 Теперь выберите Вашу должность:",
            parse_mode="Markdown",
            reply_markup=job_title_keyboard()
        )

@employee_router.callback_query(StateFilter(EmployeeStates.getting_employees_job_title))
async def start_registration(callback_query: types.CallbackQuery, state: FSMContext):
    job_title_list = [
        'driver', 'logistician', 'loader'
    ]
    job_title_to_check = callback_query.data

    if job_title_to_check not in job_title_list:
        if job_title_to_check == "back":
            # Удаляем сообщение с должностями
            await callback_query.message.delete()
            await state.set_state(EmployeeStates.getting_employees_name)
            await callback_query.message.answer(
                f"📝 Введите Ваше полное ФИО (Иванов Иван Иванович):",
                reply_markup=return_keyboard()
            )
            return
        await callback_query.message.answer(
            f"💼Выберите должность из предложенных",
            reply_markup=job_title_keyboard()
        )
        return

    # Отвечаем на callback
    await callback_query.answer()

    # Сохраняем данные пользователя в state
    await state.update_data(
        job_title=job_title_to_check
    )

    await state.set_state(EmployeeStates.getting_employees_work_number)

    await callback_query.message.answer(
        f"Отлично!\n\n"
        f"📋Пришлите ваш табельный номер для проверки администратором",
        reply_markup=back_keyboard()
    )


@employee_router.callback_query(lambda c: c.data == "back",
                                StateFilter(EmployeeStates.getting_employees_work_number))
async def back_to_job_title(callback_query: types.CallbackQuery, state: FSMContext):
    """Возврат к выбору должности"""
    await callback_query.answer()
    await state.set_state(EmployeeStates.getting_employees_job_title)

    # Удаляем предыдущее сообщение
    await callback_query.message.delete()

    await callback_query.message.answer(
        f"💼Выберите должность из предложенных",
        reply_markup=job_title_keyboard()
    )

@employee_router.message(StateFilter(EmployeeStates.getting_employees_work_number))
async def start_registration(message: types.Message, state: FSMContext, bot: Bot):
    # Сохраняем данные сотрудника в state
    try:
        employees_work_number = message.text.strip()
        if not employees_work_number.isdigit():
            raise ValueError('Некорретный ввод. Табельный номер должен состоять только из цифр. Попробуйте ввести снова')
    except ValueError as e:
        await message.answer(
            f"❌Ошибка! {e}",
            reply_markup=return_keyboard()
        )
    else:
        await state.set_state(EmployeeStates.end_registration)

        # Сохраняем данные пользователя в state
        await state.update_data(
            employees_work_number=employees_work_number
        )

        new_user_data = await state.get_data()
        user_id = message.from_user.id

        # Формируем сообщение для админа
        admin_message = (
            "👤*Новый сотрудник!*\n\n"
            f"🆔*Telegram_ID:* {new_user_data.get('clients_id', '')}\n"
            f"📝*ФИО:* {new_user_data.get('employees_name', '')}\n"
            f"💼*Длжность:* {new_user_data.get('job_title', '')}\n"
            f"🔢*Табельный номер:* {new_user_data.get('employees_work_number', '')}\n\n"
            f"❓Подтвердить регистрацию?"
        )

        # Сохраняем данные пользователя в словарь ожидающих подтверждения
        pending_registrations[user_id] = {
            'data': new_user_data,
            'state': state,
            'user_message_id': message.message_id
        }

        # отправляем сообщение админу на согласование
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode="Markdown",
                reply_markup=confirmation_keyboard(user_id)
            )
            logger.info(f"Сообщение отправлено админу {admin_id} для подтверждения регистрации пользователя {user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")
            await message.answer(
                f"❌Ошибка отправки данных администратору. Попробуйте позже.",
                reply_markup=return_keyboard()
            )
            return

        await message.answer(
            f"✅ Все необходимые данные получены и отправлены администратору на согласование!\n"
            f"📨По результатам согласования Вы получите уведомление. До встречи!",
            reply_markup=return_keyboard()
        )