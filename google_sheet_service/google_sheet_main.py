import sys
import os
import logging
from typing import List, Any
import json

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.oauth2.service_account import Credentials
import gspread

from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE
from data.database import get_all_employees
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

def clear_entire_sheet(wb, sheet_name='Данные по стотрудникам'):
    """Полностью очистить лист"""
    worksheet = wb.worksheet(sheet_name)
    worksheet.batch_clear(['A2:Z'])
    all_employees: List = get_all_employees()
    logger.info(f"✅ Лист '{sheet_name}' очищен, заголовки сохранены")

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


def synchronize():
    try:
        wb = setup_sheets_api()
        worksheet = wb.worksheet('Данные по стотрудникам')
        clear_entire_sheet(wb)
        employees = get_all_employees()

        if employees:
            for i_empl in employees:
                new_row = []
                new_row.append([i_pos for i_pos in i_empl])
                worksheet.append_row(new_row)

    except Exception as e:
        return False
    return True

if __name__ == '__main__':

    my_google_wb = setup_sheets_api()
    # some_data = menage_google_sheet(my_google_wb)
    test_google_sheet(my_google_wb)



