from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile("config.py")

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

from app.login import login_manager
login_manager.init_app(app)

from app.models import User
from app import routes
