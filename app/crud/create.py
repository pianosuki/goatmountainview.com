"""
CRUD - Create Operations

Functions for creating new records in the database.
"""

from app import db
from app.crud.helpers import get_model_class


def add_table_row(table_name: str, column_data: dict):
    """
    Add a new row to a table.
    
    Args:
        table_name: Name of the table (e.g., 'does', 'soaps')
        column_data: Dictionary of column names and values
    
    Returns:
        The newly created row object
    """
    model_class = get_model_class(table_name)
    
    if not model_class:
        raise ValueError(f"Unknown table: {table_name}")
    
    # Create and save the new row
    new_row = model_class(**column_data)
    db.session.add(new_row)
    db.session.commit()
    
    return new_row
