from aiogram.fsm.state import State, StatesGroup

# 2. Создаем класс состояний
class EmployeeStates(StatesGroup):
    """Класс для хранения состояний клиента"""
    in_employees_main_menu = State()
    wait_for_start = State()
    getting_employees_name = State()
    getting_employees_job_title = State()
    getting_employees_work_number = State()
    end_registration = State()
    getting_amount_off_spending = State()
    getting_purpose_off_spending = State()
    getting_details_off_spending = State()
    getting_month_to_show_spendings = State()

class AdminStates(StatesGroup):
    """Класс для хранения состояний админа"""
    in_admins_main_menu = State()
    getting_employees_id_to_get_spending = State()
    getting_month_to_get_spending = State()