from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker


engineB = create_engine(
    "mssql+pyodbc://@WIN-746EJ365LOT/EmployeeManagement"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

BaseB = declarative_base()
SessionB = sessionmaker(bind=engineB)
