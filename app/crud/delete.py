"""
CRUD - Delete Operations

Functions for deleting records from the database.
"""

from app import db
from app.crud.helpers import get_model_class


def delete_table_row(table_name: str, row_id: int):
    """
    Delete a row by ID.
    Also renumbers remaining rows to maintain sequential IDs.
    
    Args:
        table_name: Name of the table
        row_id: ID of the row to delete
    """
    model_class = get_model_class(table_name)
    
    if not model_class:
        raise ValueError(f"Unknown table: {table_name}")
    
    row = model_class.query.get(row_id)

    if row:
        db.session.delete(row)
        db.session.commit()
        
        # Renumber remaining rows
        remaining_rows = model_class.query.filter(model_class.id > row_id).all()
        for remaining_row in remaining_rows:
            remaining_row.id -= 1
        db.session.commit()
