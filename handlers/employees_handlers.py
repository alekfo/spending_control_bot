from config import admin_id
from keyboards.keyboards import
from states import EmployeeStates, AdminStates
from handlers.common_handlers import cancel_handler

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
employee_router = Router()

@admin_router.message(StateFilter(AdminStates.choise_action))
async def processed_admin_actions(message: types.Message, state: FSMContext):

    if message.text and message.text.lower() == "отмена":
        await cancel_handler(message, state)
        return

    if message.text == 'Выгрузка в чат':
        res = got_clients_in_chat()
        await message.answer(
            f"Последние 20 заявок:\n\n{res}",
            reply_markup=return_keyboard()
        )
        await state.set_state(AdminStates.clients_gotten)
    elif message.text == 'Выгрузка файлом':
        file_stream = await got_clients_in_file()
        if file_stream:
            # Создаем BufferedInputFile из BytesIO
            excel_file = BufferedInputFile(
                file=file_stream.getvalue(),
                filename=f"clients_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            )

            await message.answer_document(
                document=excel_file,
                caption="📊 Файл со всеми заявками",
                reply_markup=return_keyboard()
            )
        else:
            logger.error(f"Ошибка создания файла")
            await message.answer(
                "❌ Ошибка при создании файла",
                reply_markup=return_keyboard()
            )
        await state.set_state(AdminStates.clients_gotten)
    else:
        await message.answer(
            f"Пожалуйста, воспользуйтесь кнопками\n\n"
            f"Если хотите закончить нажмите на кнопку - Отмена↩️",
            reply_markup=take_admin_choise_keyboard()
        )