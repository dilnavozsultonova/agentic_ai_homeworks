from .engineB import SessionB
from .modelsB import Department,Employee,Salary
from sqlalchemy import func

class DB_B:
    def __init__(self):
        self.session = SessionB
        
    def get_employee_by_id(self,employee_id):
        session = self.session()
        try:
            employee = (
                session.query(Employee).filter_by(employee_id=employee_id).first()
            )
            
            if not employee:
                return None
            
            latest_salary = (
                session.query(Salary)
                .filter(Salary.employee_id==Employee.employee_id).
                order_by(Salary.effective_date.desc()).first()
            )

            return {
                "employee_id": Employee.employee_id,
                "name":f"{employee.first_name}{employee.last_name}",
                "department":employee.department.department_name,
                "salary":float(latest_salary.salary_amount) if latest_salary else None
            }
        finally:
            session.close()
    
    def get_employees_by_salary_desc(self, limit=5):
        session = self.session()
        try:
            query = (
                session.query(
                    Employee.employee_id,
                    Employee.first_name,
                    Employee.last_name,
                    Department.department_name,
                    Salary.salary_amount
                )
                .join(Salary, Employee.employee_id == Salary.employee_id)
                .join(Department, Employee.department_id == Department.department_id)
                .order_by(Salary.salary_amount.desc())
            )

            if limit:
                query = query.limit(limit)

            results = query.all()

            return [
                {
                    "employee_id": r.employee_id,
                    "name": f"{r.first_name} {r.last_name}",
                    "department": r.department_name,
                    "salary": float(r.salary_amount)
                }
                for r in results
            ]

        finally:
            session.close()




    def get_top_employees(self, limit):
        return self.get_employees_by_salary_desc(limit=limit)


    from sqlalchemy import func

    def get_highest_salary_per_department(self):
        session = self.session()
        try:
            subquery = (
                session.query(
                    Department.department_id,
                    func.max(Salary.salary_amount).label("max_salary")
                )
                .join(Employee, Department.department_id == Employee.department_id)
                .join(Salary, Employee.employee_id == Salary.employee_id)
                .group_by(Department.department_id)
                .subquery()
            )

            results = (
                session.query(
                    Department.department_name,
                    Employee.first_name,
                    Employee.last_name,
                    Salary.salary_amount
                )
                .join(Employee, Department.department_id == Employee.department_id)
                .join(Salary, Employee.employee_id == Salary.employee_id)
                .join(
                    subquery,
                    (Department.department_id == subquery.c.department_id) &
                    (Salary.salary_amount == subquery.c.max_salary)
                )
                .all()
            )

            return [
                {
                    "department": r.department_name,
                    "employee": f"{r.first_name} {r.last_name}",
                    "salary": float(r.salary_amount)
                }
                for r in results
            ]

        finally:
            session.close()
