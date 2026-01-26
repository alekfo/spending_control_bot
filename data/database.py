import os
from datetime import datetime, timedelta
from typing import List, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from data.models import Base, Employee, Spending

os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/bot.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def add_new_employee(telegram_id, name, job_title, employees_work_number) -> Employee:

    with SessionLocal() as session:

        employee = Employee(
            clients_telegram_id=telegram_id,
            name=name,
            job_title=job_title,
            employees_work_number=employees_work_number
        )

        session.add(employee)
        session.commit()
        session.refresh(employee)

    return employee

async def create_spending(emp_id, spending, details=None, purpose=None) -> Spending:
    with SessionLocal() as session:

        spending = Spending(
            employees_id=emp_id,
            spending=spending,
            details=details,
            purpose=purpose
        )

        session.add(spending)
        session.commit()
        session.refresh(spending)

    return spending

async def get_all_employees() -> List[Employee]:
    with SessionLocal() as session:
        employees = session.query(Employee).all()
    return employees

def does_employee_exists(clients_telegram_id):
    with SessionLocal() as session:
        employee = session.query(Employee).filter(Employee.clients_telegram_id == clients_telegram_id).one_or_none()
    return employee

def get_spending_by_name(emp_id, month_to_check):
    return f'here is spending of {emp_id} on {month_to_check} period'




