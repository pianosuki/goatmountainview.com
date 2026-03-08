"""
CRUD - Read Operations

Functions for reading/retrieving records from the database.
"""

from typing import Optional, Any
from app import db
from app.crud.helpers import get_model_class


def get_all_tables() -> dict:
    """Get information about all tables in the database."""
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    tables = {}

    for table_name, table_obj in metadata.tables.items():
        tables[table_name] = get_table(table_name)

    return tables


def get_table(table_name: str) -> dict:
    """Get information about a specific table."""
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    table_obj = metadata.tables[table_name]
    columns = [column.name for column in table_obj.columns]
    optional_columns = [column.name for column in table_obj.columns if column.nullable]
    rows_list = get_table_rows(table_name)
    
    return {
        "table_name": table_name,
        "table_columns": columns,
        "optional_columns": optional_columns,
        "table_rows": rows_list
    }


def get_table_rows(table_name: str) -> list:
    """Get all rows from a table."""
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    table_obj = metadata.tables[table_name]
    columns = [column.name for column in table_obj.columns]
    rows = db.session.query(*[getattr(table_obj.columns, column) for column in columns]).all()
    rows_list = [[getattr(row, column) for column in columns] for row in rows]

    # Mask passwords
    for column_index, column in enumerate(columns):
        if column == "password":
            for row_index, row in enumerate(rows_list):
                rows_list[row_index][column_index] = "**********"

    return rows_list


def get_table_row(table_name: str, row_id: int) -> dict:
    """Get a specific row by ID."""
    model_class = get_model_class(table_name)
    if not model_class:
        return {}
    
    row = model_class.query.get(row_id)
    if not row:
        return {}
    
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def get_table_row_column(table_name: str, row_id: int, column_name: str) -> Optional[Any]:
    """Get a specific column value from a row."""
    model_class = get_model_class(table_name)
    if not model_class:
        return None
    
    row = model_class.query.get(row_id)
    if not row:
        return None
    
    return getattr(row, column_name, None)


def search_table_row(table_name: str, filter_columns: dict) -> Optional[dict]:
    """Search for a row matching the given criteria."""
    model_class = get_model_class(table_name)
    if not model_class:
        return None
    
    conditions = []
    for column_name, column_value in filter_columns.items():
        conditions.append(f"{column_name} = :{column_name}")

    condition_string = " AND ".join(conditions)
    row = model_class.query.filter(db.text(condition_string)).params(**filter_columns).first()

    if row:
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}
    
    return None
