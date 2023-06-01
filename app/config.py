from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = "sqlite:///storage.db"
STATIC_FOLDER = "/app/static"

if SECRET_KEY is None:
    raise ValueError("Missing SECRET_KEY environment variable")
