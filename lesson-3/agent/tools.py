from google.genai import types
from db.repositoryB import DB_B


def create_db_tools(db: DB_B):
    """
    Creates STRICT database tools.
    These tools MUST be used for any employee/salary-related questions.
    """

    get_employee_by_id_tool = types.FunctionDeclaration(
        name="get_employee_by_id",
        description=(
            """Fetches FULL employee information FROM THE COMPANY DATABASE 
            using a specific employee ID. """

        ),
        parameters={
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "integer",
                    "description": "The unique ID of the employee in the company database"
                }
            },
            "required": ["employee_id"]
        }
    )

    get_top_employees_tool = types.FunctionDeclaration(
        name="get_top_employees",
        description=(
            "Returns the TOP highest-paid employees FROM THE COMPANY DATABASE. "
        ),
        parameters={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of employees to return. If not provided, return 10."
                }
            }
        }
    )

    highest_salary_per_department_tool = types.FunctionDeclaration(
        name="get_highest_salary_per_department",
        description=(
            "Returns the highest-paid employee in EACH department "
        ),
        parameters={
            "type": "object",
            "properties": {}
        }
    )

    def get_employee_by_id(args):
        return db.get_employee_by_id(args["employee_id"])

    def get_top_employees(args):
        limit = args.get("limit", 10) if args else 10
        return db.get_top_employees(limit)

    def highest_salary_per_department():
        return db.get_highest_salary_per_department()

    handlers = {
        "get_employee_by_id": get_employee_by_id,
        "get_top_employees": get_top_employees,
        "get_highest_salary_per_department": highest_salary_per_department
    }

    tools = [
        get_employee_by_id_tool,
        get_top_employees_tool,
        highest_salary_per_department_tool
    ]

    return tools, handlers
