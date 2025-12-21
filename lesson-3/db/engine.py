from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine(
    "mssql+pyodbc://@WIN-746EJ365LOT/DBName"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

