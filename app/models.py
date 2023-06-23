from datetime import datetime
from flask_login import UserMixin
from app import db
import app.crud as crud

__all__ = ["User", "Soap", "Image", "Inquiry", "Book", "Goat", "Doe", "Foundation"]


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


class Soap(db.Model):
    __tablename__ = "soaps"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    ingredients = db.Column(db.Text(), nullable=False)
    weight = db.Column(db.Float(), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=1)
    image = db.relationship("Image", backref="soap", foreign_keys="Soap.image_id")

    @staticmethod
    def filter_input_columns(column_data: dict) -> dict:
        for column_name, column_value in column_data.items():
            match column_name:
                case "image_id":
                    if isinstance(column_value, str):
                        if column_value:
                            column_data[column_name] = crud.image_id_from_string(column_value)
                        else:
                            column_data[column_name] = Soap.image_id.default.arg
                case _:
                    pass
        return column_data


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    directory = db.Column(db.String(100), default="")
    note = db.Column(db.Text())
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"))
    soap_id = db.Column(db.Integer, db.ForeignKey("soaps.id"))

    @property
    def path(self):
        return self.directory + "/" + self.filename if self.directory else self.filename

    @staticmethod
    def filter_input_columns(column_data: dict) -> dict:
        for column_name, column_value in column_data.items():
            match column_name:
                case "goat_id" | "soap_id":
                    if column_value:
                        column_data[column_name] = int(column_value)
                    else:
                        column_data[column_name] = None
                case _:
                    pass
        return column_data


class Inquiry(db.Model):
    __tablename__ = "inquiries"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    @staticmethod
    def filter_input_columns(column_data: dict) -> dict:
        for column_name, column_value in column_data.items():
            match column_name:
                case "date":
                    column_data[column_name] = datetime.strptime(column_value, "%Y-%m-%dT%H:%M:%S")
                case _:
                    pass
        return column_data


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    editors = db.Column(db.Text(), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(200), nullable=False)


class Goat(db.Model):
    __tablename__ = "goats"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    images = db.relationship("Image", backref="goat", lazy="dynamic")


class Doe(db.Model):
    __tablename__ = "does"
    id = db.Column(db.Integer, primary_key=True)
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.String(200))
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=2)
    goat = db.relationship("Goat", backref="doe", foreign_keys="Doe.goat_id")
    image = db.relationship("Image", backref="doe", foreign_keys="Doe.image_id")

    @staticmethod
    def filter_input_columns(column_data: dict) -> dict:
        for column_name, column_value in column_data.items():
            match column_name:
                case "image_id":
                    if isinstance(column_value, str):
                        if column_value:
                            column_data[column_name] = crud.image_id_from_string(column_value)
                        else:
                            column_data[column_name] = Doe.image_id.default.arg
                case "goat_id":
                    if isinstance(column_value, str):
                        if column_value:
                            column_data[column_name] = crud.goat_id_from_string(column_value)
                        else:
                            raise ValueError(f"Column '{column_name}' is required")
                case _:
                    pass
        return column_data


class Foundation(db.Model):
    __tablename__ = "foundation"
    id = db.Column(db.Integer, primary_key=True)
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"))
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.String(200))
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=2)
    goat = db.relationship("Goat", backref="foundation", foreign_keys="Foundation.goat_id")
    image = db.relationship("Image", backref="foundation", foreign_keys="Foundation.image_id")

    @staticmethod
    def filter_input_columns(column_data: dict) -> dict:
        for column_name, column_value in column_data.items():
            match column_name:
                case "image_id":
                    if isinstance(column_value, str):
                        if column_value:
                            column_data[column_name] = crud.image_id_from_string(column_value)
                        else:
                            column_data[column_name] = Foundation.image_id.default.arg
                case "goat_id":
                    if isinstance(column_value, str):
                        if column_value:
                            column_data[column_name] = crud.goat_id_from_string(column_value)
                        else:
                            raise ValueError(f"Column '{column_name}' is required")
                case _:
                    pass
        return column_data
