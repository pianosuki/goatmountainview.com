from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = "sqlite:///storage.db"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, "static")
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static", "images", "uploads")
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

if SECRET_KEY is None:
    raise ValueError("Missing SECRET_KEY environment variable")
