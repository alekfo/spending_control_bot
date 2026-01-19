from config import admin_id
from keyboards.main_keyboards import return_keyboard
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler
from google_sheet_service.google_sheet_main import get_all_employees

from datetime import datetime
import openpyxl
from io import BytesIO
import logging
from aiogram import types, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import SQLAlchemyError
from aiogram.types import FSInputFile, BufferedInputFile

from aiogram.types import ReplyKeyboardRemove

logger = logging.getLogger(__name__)
admin_router = Router()

@admin_router.callback_query(lambda c: c.data == "get_all_empoyees", AdminStates.in_admins_main_menu)
async def process_continue(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик callback-запроса от кнопки "Все сотрудники"
    только в состоянии AdminStates.in_admins_main_menu
    """

    # Отвечаем на callback, чтобы убрать "часики" у кнопки
    await callback_query.answer()
    await state.set_state(UserStates.in_basic)

    result = get_all_employees()

    # Отправляем новое сообщение
    await callback_query.message.answer(
        f"Все сотрудники:\n{result}",
        reply_markup=return_keyboard()
    )