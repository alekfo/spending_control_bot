import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE
import json

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
        print("✅ Успешно подключились к таблице!")
        return wb
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

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


def menage_google_sheet(wb, sheet_name='Данные по стотрудникам'):
    """Чтение данных из таблицы"""
    # Получаем нужный лист
    worksheet = wb.worksheet(sheet_name)

    # 1. Считываем все строки (со 2 строки)
    all_data = worksheet.get_all_values()

if __name__ == '__main__':

    my_google_wb = setup_sheets_api()
    # some_data = menage_google_sheet(my_google_wb)
    test_google_sheet(my_google_wb)

def does_employee_exists(employees_id):
    wb = setup_sheets_api()
    return True

def get_all_employees():
    return "here are all employees"

def get_spending_by_name(emp_id, month_to_check):
    return f'here is spending of {emp_id} on {month_to_check} period'

def add_new_employee(user_id, full_name, job_title, work_number):
    return True