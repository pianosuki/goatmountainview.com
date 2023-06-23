import os
from typing import Optional, Any
from app import app, db
from app.models import *
from app.utils import split_file_path


# Utils #
def table_to_model(table_name: str) -> Optional[str]:
    name_mapping = {mapper.class_.__tablename__: mapper.class_.__name__ for mapper in db.Model.registry.mappers}
    return name_mapping.get(table_name, None)


def column_is_nullable(table_name: str, column_name: str) -> bool:
    model_class = globals()[table_to_model(table_name)]
    return getattr(model_class, column_name).nullable


def image_id_from_string(id_string: str) -> int:
    try:
        image_id = int(id_string)
        if not Image.query.get(id_string):
            raise IndexError(f"The image with ID ({id_string}) doesn't exist")
    except ValueError:
        directory, filename = split_file_path(id_string)
        image = Image.query.filter_by(filename=filename, directory=directory).first()
        if not image:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file '{os.path.join(directory, filename)}' was not found")
            image = Image(filename=filename, directory=directory)
            db.session.add(image)
            db.session.commit()
        image_id = image.id
    return image_id


def goat_id_from_string(id_string: str) -> int:
    try:
        image_id = int(id_string)
        if not Goat.query.get(id_string):
            raise IndexError(f"The goat with ID ({id_string}) doesn't exist")
    except ValueError:
        goat = Goat.query.filter_by(name=id_string).first()
        if not goat:
            goat = Goat(name=id_string)
            db.session.add(goat)
            db.session.commit()
        image_id = goat.id
    return image_id


# Create #
def add_table_row(table_name: str, column_data: dict):
    model_class = globals()[table_to_model(table_name)]
    if getattr(model_class, "filter_input_columns", False):
        column_data = model_class.filter_input_columns(column_data)
    new_row = model_class(**column_data)
    db.session.add(new_row)
    db.session.commit()


# Read #
def get_all_tables() -> dict:
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    tables = {}
    for table_name, table_obj in metadata.tables.items():
        tables[table_name] = get_table(table_name)
    return tables


def get_table(table_name: str) -> dict:
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    table_obj = metadata.tables[table_name]
    columns = [column.name for column in table_obj.columns]
    optional_columns = [column.name for column in table_obj.columns if column.nullable]
    rows_list = get_table_rows(table_name)
    table_info = {
        "table_name": table_name,
        "table_columns": columns,
        "optional_columns": optional_columns,
        "table_rows": rows_list
    }
    return table_info


def get_table_rows(table_name: str) -> list:
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    table_obj = metadata.tables[table_name]
    columns = [column.name for column in table_obj.columns]
    rows = db.session.query(*[getattr(table_obj.columns, column) for column in columns]).all()
    rows_list = [[getattr(row, column) for column in columns] for row in rows]
    for column_index, column in enumerate(columns):
        if column == "password":
            for row_index, row in enumerate(rows_list):
                rows_list[row_index][column_index] = "**********"
    return rows_list


def get_table_row(table_name: str, row_id: int) -> dict:
    model_class = globals()[table_to_model(table_name)]
    row = model_class.query.get(row_id)
    row_dict = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    return row_dict


def get_table_row_column(table_name: str, row_id: int, column_name: str) -> Optional[Any]:
    model_class = globals()[table_to_model(table_name)]
    row = model_class.query.get(row_id)
    column = getattr(row, column_name, None)
    return column


def search_table_row(table_name: str, filter_columns: dict) -> Optional[dict]:
    model_class = globals()[table_to_model(table_name)]
    conditions = []
    for column_name, column_value in filter_columns.items():
        condition = f"{column_name} = :{column_name}"
        conditions.append(condition)
    condition_string = " AND ".join(conditions)
    row = model_class.query.filter(db.text(condition_string)).params(**filter_columns).first()
    if row:
        row_dict = {column.name: getattr(row, column.name) for column in row.__table__.columns}
        return row_dict
    else:
        return None


# Update #
def edit_table_row(table_name: str, row_id: int, column_data: dict):
    model_class = globals()[table_to_model(table_name)]
    if getattr(model_class, "filter_input_columns", False):
        column_data = model_class.filter_input_columns(column_data)
    row = model_class.query.get(row_id)
    if row:
        for column, value in column_data.items():
            setattr(row, column, value)
        db.session.commit()


# Delete #
def delete_table_row(table_name: str, row_id: int):
    model_class = globals()[table_to_model(table_name)]
    row = model_class.query.get(row_id)
    if row:
        db.session.delete(row)
        db.session.commit()
        remaining_rows = model_class.query.filter(model_class.id > row_id).all()
        for remaining_row in remaining_rows:
            remaining_row.id -= 1
        db.session.commit()
