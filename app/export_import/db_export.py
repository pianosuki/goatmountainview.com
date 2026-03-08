"""
Database Export Module

Exports database to JSON format for backup.
"""

import json
from datetime import datetime
import app.crud as crud
from app.export_import.config import EXPORT_IMPORT_TABLES


def export_database() -> dict:
    """
    Export entire database to a dictionary structure.
    Returns data in a format suitable for JSON export.
    """
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "version": "1.0",
        "tables": {}
    }

    for table_name in EXPORT_IMPORT_TABLES:
        try:
            table_data = export_table(table_name)
            if table_data:
                export_data["tables"][table_name] = table_data
        except Exception as e:
            print(f"Error exporting {table_name}: {e}")
            continue

    return export_data


def export_table(table_name: str) -> dict:
    """
    Export a single table to dictionary format.
    Handles special field conversions for portability.
    """
    model_class = crud.get_model_class(table_name)
    if not model_class:
        return {}

    # Get rows and colum names
    rows = model_class.query.all()
    columns = [column.name for column in model_class.__table__.columns]
    
    exported_rows = []

    # Export rows
    for row in rows:
        row_dict = {}
        for column in columns:
            value = getattr(row, column, None)
            
            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            
            # Skip passwords for security
            if column == "password":
                continue
            
            row_dict[column] = value
        
        exported_rows.append(row_dict)
    
    return {
        "columns": columns,
        "row_count": len(exported_rows),
        "data": exported_rows
    }


def export_to_json_file(filepath: str) -> bool:
    """
    Export database to a JSON file.
    Returns True if successful.
    """
    try:
        export_data = export_database()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False
