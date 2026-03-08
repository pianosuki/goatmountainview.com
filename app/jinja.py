from typing import Optional, List
from datetime import datetime
from app.models import Image, Goat
from app.field_mappings import DISPLAY_FIELDS, DISPLAY_COLUMNS
import app.crud as crud


def extend_env(env):
    env.filters["split_string"] = split_string
    env.globals["find_item_index"] = find_item_index
    env.globals["column_is_nullable"] = crud.column_is_nullable
    env.globals["get_table_row_column"] = crud.get_table_row_column
    env.globals["current_date_time"] = current_date_time
    env.globals["slideshow_speed_constant"] = 128
    env.globals["get_image_url"] = get_image_url
    env.globals["get_image_by_id"] = get_image_by_id
    env.globals["enumerate"] = enumerate
    env.globals["get_display_columns"] = get_display_columns
    env.globals["get_user_fields"] = get_user_fields
    env.globals["get_image_id_for_row"] = get_image_id_for_row
    env.globals["get_row_value"] = get_row_value
    env.globals["get_all_images"] = get_all_images
    env.globals["get_field_value"] = get_field_value
    env.globals["get_image_id_for_record"] = get_image_id_for_record
    env.globals["get_display_value_for_row"] = get_display_value_for_row


def split_string(value, delimiter) -> List[str]:
    return value.split(delimiter)


def find_item_index(items: list, item_name: str) -> Optional[int]:
    index = None
    for i, item in enumerate(items):
        if item == item_name:
            index = i
            break
    return index


def current_date_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_image_url(image_row) -> Optional[str]:
    """Generate URL for an image from a row dict or Image object"""
    if isinstance(image_row, dict):
        filename = image_row.get("filename", "")
        directory = image_row.get("directory", "")
    elif isinstance(image_row, Image):
        filename = image_row.filename
        directory = image_row.directory
    else:
        return None
    
    if not filename:
        return None
    
    if directory:
        return f"/static/images/uploads/{directory}/{filename}"
    else:
        return f"/static/images/uploads/{filename}"


def get_image_by_id(image_id) -> Optional[Image]:
    """Get Image object by ID"""
    if image_id:
        try:
            return Image.query.get(int(image_id))
        except (ValueError, TypeError):
            return None
    return None


def get_all_images() -> List[Image]:
    """Get all images for the image browser"""
    return Image.query.all()


def get_display_columns(table_name: str) -> List[str]:
    """Get user-friendly column names to display in table (hide technical fields)"""
    return DISPLAY_COLUMNS.get(table_name, ["name"])


def get_user_fields(table_name: str) -> List[dict]:
    """Get simplified form fields for adding/editing (hide technical database fields)"""
    return DISPLAY_FIELDS.get(table_name, [])


def get_image_id_for_row(row: list, table_name: str) -> Optional[int]:
    """Get the image ID for a table row"""
    # Get the column names for this table
    from app import crud
    try:
        table_info = crud.get_table(table_name)
        columns = table_info.get("table_columns", [])
        
        # Find the image_id column index
        if "image_id" in columns:
            img_index = columns.index("image_id")
            if img_index < len(row):
                img_id = row[img_index]
                # Make sure it's actually an integer (not a URL or other data)
                if img_id is not None:
                    try:
                        return int(img_id)
                    except (ValueError, TypeError):
                        return None
    except Exception:
        pass
    
    return None


def get_row_value(row: list, column: str, all_columns: List[str]) -> Optional[str]:
    """Get a specific column value from a row"""
    try:
        index = all_columns.index(column)
        if index < len(row):
            value = row[index]
            # Format date nicely
            if column == "date" and value:
                return value.strftime("%Y-%m-%d %H:%M") if hasattr(value, "strftime") else str(value)
            return value
    except (ValueError, IndexError):
        pass
    return None


def get_display_value_for_row(row: list, column: str, table_name: str) -> Optional[str]:
    """Get display value for a column, with special handling for related data"""
    # Special handling for "name" column in tables that link to goats
    if column == "name" and table_name in ["does", "foundation", "adoptions"]:
        try:
            columns = crud.get_table(table_name).get("table_columns", [])
            if "goat_id" in columns:
                goat_id_index = columns.index("goat_id")
                goat_id = row[goat_id_index]
                if goat_id:
                    goat = Goat.query.get(int(goat_id))
                    if goat:
                        return goat.name
        except Exception:
            pass
        return "Unknown"
    
    # Default: get value from row
    return get_row_value(row, column, crud.get_table(table_name).get("table_columns", []))


def get_field_value(table_name: str, row_id: int, field_name: str) -> Optional[str]:
    """Get current value for a field when editing"""
    # Special handling for "name" field in goat-related tables
    if field_name == "name" and table_name in ["does", "foundation", "adoptions"]:
        # Get the goat_id from the record
        goat_id = crud.get_table_row_column(table_name, row_id, "goat_id")
        if goat_id:
            goat = Goat.query.get(int(goat_id))
            if goat:
                return goat.name
        return None
    
    return crud.get_table_row_column(table_name, row_id, field_name)


def get_image_id_for_record(table_name: str, row_id: int) -> Optional[int]:
    """Get the image ID for a record being edited"""
    # Map table names to their image column
    image_column_map = {
        "soaps": "image_id",
        "does": "image_id",
        "foundation": "image_id",
        "adoptions": "image_id",
    }
    
    image_col = image_column_map.get(table_name)
    if image_col:
        return crud.get_table_row_column(table_name, row_id, image_col)
    return None
