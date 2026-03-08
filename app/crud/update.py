"""
CRUD - Update Operations

Functions for updating existing records in the database.
"""

from app import db
from app.crud.helpers import get_model_class


def edit_table_row(table_name: str, row_id: int, column_data: dict):
    """
    Edit an existing row.
    
    Args:
        table_name: Name of the table
        row_id: ID of the row to edit
        column_data: Dictionary of columns and new values
    """
    model_class = get_model_class(table_name)
    
    if not model_class:
        raise ValueError(f"Unknown table: {table_name}")
    
    row = model_class.query.get(row_id)
    
    if row:
        for column, value in column_data.items():
            setattr(row, column, value)
        db.session.commit()
