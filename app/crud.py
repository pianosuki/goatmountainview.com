from app import db
from app.models import *
from app.utils import table_to_model


# Create #
def add_table_row(table_name: str, column_data: dict):
    model_class = globals()[table_to_model(table_name)]
    new_row = model_class(**column_data)
    db.session.add(new_row)
    db.session.commit()


# Read #
def get_all_tables() -> dict:
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    tables = {}
    for table_name, table_obj in metadata.tables.items():
        columns = [column.name for column in table_obj.columns]
        rows_list = get_table_rows(table_name)
        table_info = {
            "table_name": table_name,
            "table_columns": columns,
            "table_rows": rows_list
        }
        tables[table_name] = table_info
    return tables


def get_table_rows(table_name) -> list:
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


# Update #
def edit_table_row(table_name: str, row_id: int, column_data: dict):
    model_class = globals()[table_to_model(table_name)]
    row = model_class.query.get(row_id)
    if row:
        for column, value in column_data.items():
            setattr(row, column, value)
        db.session.commit()


# Delete #
def delete_table_row(table_name, row_id):
    model_class = globals()[table_to_model(table_name)]
    row = model_class.query.get(row_id)
    if row:
        db.session.delete(row)
        db.session.commit()
        remaining_rows = model_class.query.filter(model_class.id > row_id).all()
        for remaining_row in remaining_rows:
            remaining_row.id -= 1
        db.session.commit()
