from aiogram.fsm.state import State, StatesGroup

# 2. Создаем класс состояний
class EmployeeStates(StatesGroup):
    """Класс для хранения состояний клиента"""
    wait_for_start = State()

class AdminStates(StatesGroup):
    """Класс для хранения состояний админа"""
    in_admins_main_menu = State()