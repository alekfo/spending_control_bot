from keyboards.admin_keyboards import admins_main_menu_keyboard
from keyboards.employees_keyboards import employees_main_menu_keyboard
from keyboards.main_keyboards import start_registration_keyboard
from states import EmployeeStates, AdminStates
from config import admin_id
from data.database import does_employee_exists

import logging
from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart


logger = logging.getLogger(__name__)
common_router = Router()
cancel_router = Router()

# ADMIN_IDS = [admin_id, admin_id_main]

@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Этот обработчик срабатывает на команду /start и при первом входе
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if user_id == admin_id:
        await message.answer(
            f'👨‍💼 *Вы — администратор системы*\n\n'
            f'🚀 Выберите действие:',
            parse_mode="Markdown",
            reply_markup=admins_main_menu_keyboard()
        )
        await state.set_state(AdminStates.in_admins_main_menu)
        return

    # Сохраняем данные пользователя в state
    await state.update_data(
        clients_id=user_id
    )

    # Проверяем, существует ли пользователь в БД
    user_name = does_employee_exists(user_id)

    if user_name:
        await message.answer(
            f'👋 *С вовзращением!*\n\n'
            f'💼 Выберите действие в системе:',
            parse_mode="Markdown",
            reply_markup=employees_main_menu_keyboard()
        )
        await state.set_state(EmployeeStates.in_employees_main_menu)
        return
    else:
        # Получаем текущее состояние пользователя
        current_state = await state.get_state()
        if current_state == EmployeeStates.end_registration.state:
            await message.answer(
                '👋 *Дождитесь подтверждения регистрации от администратора. Спасибо!*\n'
            )
            return

        await message.answer(
            '👋 *Добро пожаловать в чат-бот контроля расходов отдела логистики VooMoo!*\n\n'
            '📝 Для работы в системе необходимо пройти регистрацию',
            parse_mode="Markdown",
            reply_markup=start_registration_keyboard()
        )
        await state.set_state(EmployeeStates.wait_for_start)
        # Логируем нового пользователя
        logger.info(f'Новый пользователь бота: user_name: {user_name}, user_id {user_id}')



@common_router.message(StateFilter(None))
async def handle_any_message(message: types.Message, state: FSMContext):
    """Обработчик любых сообщений без состояния"""
    await cmd_start(message, state)


@cancel_router.message(Command("cancel"))
@cancel_router.message(lambda message: message.text == "🤖Главное меню")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Сброс состояния"""
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await cmd_start(message, state)