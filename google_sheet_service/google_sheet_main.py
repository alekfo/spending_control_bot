import sys
import os
import logging
from typing import List, Any
import json
import asyncio

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.oauth2.service_account import Credentials
import gspread

from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE
from data.database import get_all_employees, get_all_spendings
from data.models import Employee, Spending

logger = logging.getLogger(__name__)

def setup_sheets_api():

    # 3. Настройка областей доступа
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # 4. Авторизация
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    gc = gspread.authorize(credentials)

    # 5. Открытие таблицы
    try:
        wb = gc.open_by_key(SPREADSHEET_ID)
        logger.info("✅ Успешно подключились к таблице!")
        return wb
    except Exception as e:
        logger.warning(f"❌ Ошибка подключения: {e}")
        return None

def clear_entire_sheet(worksheet):
    """Полностью очистить лист"""
    worksheet.batch_clear(['A2:Z'])
    logger.info(f"✅ Лист '{worksheet.title}' очищен, заголовки сохранены")

def test_google_sheet(wb):

    worksheet = wb.worksheet('Данные по стотрудникам')
    all_data = worksheet.get_all_values()
    print(all_data)

    new_row = [
        "Комлов Валера",
        "Водитель",
       "1488"
    ]

    # Добавляем новую строку
    worksheet.append_row(new_row)

    # Способ 1: Изменить ячейку по номеру строки и столбца
    # (нумерация начинается с 1)
    worksheet.update_cell(2, 1, "Алексеев Алексей")  # Строка 2, Колонка A -> "Новое имя"
    worksheet.update_cell(2, 3, "121418994")  # Строка 2, Колонка C -> "999999"

async def filling_in_employees_shеet(worksheet):
    employees = await get_all_employees()

    if employees:
        for employee in employees:
            row_data = [
                employee.id,
                employee.name,
                employee.clients_telegram_id,
                employee.job_title,
                str(employee.employees_work_number)
            ]
            worksheet.append_row(row_data)
    return len(employees)

async def filling_in_spendings_shеet(worksheet):
    spendings = await get_all_spendings()

    if spendings:
        for spending in spendings:
            date_str = spending.date_of_spending.strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                spending.id,
                spending.employees_id,
                spending.spending,
                spending.purpose,
                spending.details,
                date_str
            ]
            worksheet.append_row(row_data)

    return len(spendings)

async def synchronize():
    try:
        wb = setup_sheets_api()
        worksheet_emp = wb.worksheet('Данные по стотрудникам')
        worksheet_spend = wb.worksheet('Расходы')
        clear_entire_sheet(worksheet_emp)
        clear_entire_sheet(worksheet_spend)

        employees_count = await filling_in_employees_shеet(worksheet_emp)
        spendings_count = await filling_in_spendings_shеet(worksheet_spend)

        logger.info(f"✅ Синхронизация завершена. Добавлено {employees_count} сотрудников и {spendings_count} расходов")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка синхронизации: {e}")
        raise e

if __name__ == '__main__':

    my_google_wb = setup_sheets_api()
    # some_data = menage_google_sheet(my_google_wb)
    test_google_sheet(my_google_wb)



