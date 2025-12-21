from app.application import Application
from db.engine import engine, Base
from dotenv import load_dotenv

load_dotenv(".env")

Base.metadata.create_all(engine)

app = Application()
app.run()
