import os
import json
from collections import OrderedDict
from dotenv import load_dotenv
from app import app, db, bcrypt
from app.models import *
import app.crud as crud


def setup():
    with app.app_context():
        os.makedirs(app.config["STATIC_FOLDER"] + "/images/books", exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"] + "/soap", exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"] + "/does", exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"] + "/adoptions", exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"] + "/foundation", exist_ok=True)
        db_file = "instance/" + app.config["SQLALCHEMY_DATABASE_URI"].split("///")[1]
        if not os.path.exists(db_file):
            db.create_all()
            load_dotenv()
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
            if username is None or password is None:
                raise ValueError("Missing USERNAME and/or PASSWORD environment variables")
            if not User.query.filter_by(username=username).first():
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                user = User(username=username, password=hashed_password)
                db.session.add(user)
                db.session.commit()
            with open("app/defaults.json", "r") as tables:
                table_data = json.load(tables, object_pairs_hook=OrderedDict)
                for key, row_data in table_data.items():
                    for column_data in row_data:
                        crud.add_table_row(key, column_data)
        else:
            db.create_all()
