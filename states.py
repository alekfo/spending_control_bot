from aiogram.fsm.state import State, StatesGroup

# 2. Создаем класс состояний
class EmployeeStates(StatesGroup):
    """Класс для хранения состояний клиента"""
    wait_for_start = State()
    getting_employees_name = State()
    getting_employees_job_title = State()
    getting_employees_work_number = State()
    end_registration = State()

class AdminStates(StatesGroup):
    """Класс для хранения состояний админа"""
    in_admins_main_menu = State()
    getting_all_employees = State()
    getting_employees_id_to_get_spending = State()
    getting_month_to_get_spending = State()
    getting_employee_spending = State()