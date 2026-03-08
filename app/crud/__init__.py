"""
CRUD Package

Database operations organized by category.
"""

from app.crud.helpers import (
    get_model_class,
    column_is_nullable,
    image_id_from_string,
    goat_id_from_string
)

from app.crud.create import add_table_row
from app.crud.read import (
    get_all_tables,
    get_table,
    get_table_rows,
    get_table_row,
    get_table_row_column,
    search_table_row
)
from app.crud.update import edit_table_row
from app.crud.delete import delete_table_row

__all__ = [
    # Helpers
    "get_model_class",
    "column_is_nullable",
    "image_id_from_string",
    "goat_id_from_string",
    
    # Create
    "add_table_row",
    
    # Read
    "get_all_tables",
    "get_table",
    "get_table_rows",
    "get_table_row",
    "get_table_row_column",
    "search_table_row",
    
    # Update
    "edit_table_row",
    
    # Delete
    "delete_table_row"
]
