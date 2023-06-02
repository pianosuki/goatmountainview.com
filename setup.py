from dotenv import load_dotenv
import os
from app import app, db, bcrypt
from app.models import User


def setup():
    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
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
        else:
            db.create_all()
