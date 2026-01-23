from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    clients_telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(50))
    job_title = Column(String(100))
    employees_work_number = Column(String(100))

    spendings = relationship("Spending", cascade='all, delete-orphan')

    def __repr__(self):
        return (f"<Employee(id={self.id}, "
                f"telegram_id={self.clients_telegram_id}, "
                f"name='{self.name}', "
                f"job_title='{self.job_title}')>")


class Spending(Base):
    __tablename__ = "spendings"

    id = Column(Integer, primary_key=True)
    employees_id = Column(Integer, ForeignKey('employees.id'))
    spending = Column(String(50), nullable=False)
    details = Column(String(500))
    purpose = Column(String(500))
    date_of_spending = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return (f"<Spending(id={self.id}, "
                f"employee_id={self.employees_id}, "
                f"spending='{self.spending}', "
                f"date='{self.date_of_spending}')>")