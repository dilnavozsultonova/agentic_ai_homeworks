from sqlalchemy import String, DateTime, ForeignKey,Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .engineB import BaseB
from decimal import Decimal

class Department(BaseB):
    __tablename__ = "Departments"
    department_id:Mapped[int] = mapped_column(primary_key=True)
    department_name:Mapped[str] = mapped_column(String(100),unique=True,nullable=False)

    employees = relationship("Employee", back_populates="department")



class Employee(BaseB):
    __tablename__ = "Employees"
    employee_id:Mapped[int] = mapped_column(primary_key=True)
    first_name:Mapped[str] = mapped_column(String(50),nullable=False)
    last_name:Mapped[str] = mapped_column(String(50),nullable=False)
    department_id:Mapped[int] = mapped_column(
        ForeignKey("Departments.department_id"),
        nullable=False
    )
    hire_date:Mapped[DateTime] = mapped_column(DateTime,nullable=False)

    department = relationship("Department", back_populates="employees")
    salaries = relationship("Salary", back_populates="employee")


class Salary(BaseB):
    __tablename__ = "Salaries"
    salary_id:Mapped[int] = mapped_column(primary_key=True,nullable=False)
    employee_id:Mapped[int] = mapped_column(
        ForeignKey("Employees.employee_id"),
        nullable=False
    )
    salary_amount:Mapped[Decimal] = mapped_column(Numeric(10,2),nullable=False)
    effective_date:Mapped[DateTime] = mapped_column(DateTime,nullable=False)

    employee = relationship("Employee", back_populates="salaries")


