from dotenv import load_dotenv
import os
from urllib.parse import urlsplit

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
# Use one preferred origin even when visitors arrive through EditorMelinda.com.
SITE_URL = os.getenv("SITE_URL", "https://goatmountainview.com").rstrip("/")
site_url_parts = urlsplit(SITE_URL)
if (site_url_parts.scheme not in {"http", "https"} or not site_url_parts.hostname
        or site_url_parts.path or site_url_parts.query or site_url_parts.fragment
        or site_url_parts.username or site_url_parts.password):
    raise ValueError("SITE_URL must be an absolute http(s) origin without a path")
SQLALCHEMY_DATABASE_URI = "sqlite:///storage.db"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, "static")
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static", "images", "uploads")
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

if SECRET_KEY is None:
    raise ValueError("Missing SECRET_KEY environment variable")
