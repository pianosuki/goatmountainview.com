from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile("config.py")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Initialize login manager
from app.login import login_manager
login_manager.init_app(app)

# Import and register all routes
from app import routes

# Jinja extensions
from app.jinja import extend_env
extend_env(app.jinja_env)
