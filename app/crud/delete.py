"""
CRUD - Delete Operations

Functions for deleting records from the database.
"""

from app import db
from app.crud.helpers import get_model_class


def delete_table_row(table_name: str, row_id: int):
    """
    Delete a row by ID.

    Note: IDs are NOT renumbered after deletion to preserve referential integrity.
    Foreign key references (e.g., image_id in soaps/does/foundation tables) must remain stable.

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
