"""
Database Import Module

Imports database from JSON backup files.
"""

import json
from datetime import datetime
from app import db
import app.crud as crud
from app.export_import.config import EXPORT_IMPORT_TABLES


def import_database(export_data: dict) -> dict:
    """
    Import database from exported dictionary.
    Returns statistics about the import.
    """
    stats = {
        "tables_imported": 0,
        "rows_imported": 0,
        "errors": []
    }

    if "tables" not in export_data:
        stats["errors"].append("Invalid export format: missing 'tables' key")
        return stats

    for table_name in EXPORT_IMPORT_TABLES:
        if table_name in export_data["tables"]:
            try:
                table_stats = import_table(table_name, export_data["tables"][table_name])
                stats["tables_imported"] += 1
                stats["rows_imported"] += table_stats.get("rows_imported", 0)
                if table_stats.get("errors"):
                    stats["errors"].extend(table_stats["errors"])
            except Exception as e:
                stats["errors"].append(f"Error importing {table_name}: {str(e)}")

    stats["notes"] = ["Users table was not imported (passwords cannot be imported for security)"]

    return stats


def import_table(table_name: str, table_data: dict) -> dict:
    """
    Import a single table from exported data.
    Handles special field conversions.
    """
    stats = {
        "rows_imported": 0,
        "errors": []
    }
    
    model_class = crud.get_model_class(table_name)
    if not model_class:
        stats["errors"].append(f"Unknown table: {table_name}")
        return stats
    
    # Clear existing data (except users table)
    if table_name != "users":
        try:
            db.session.query(model_class).delete()
            db.session.commit()
        except Exception as e:
            stats["errors"].append(f"Could not clear {table_name}: {str(e)}")
            return stats
    
    # Import rows
    for row_data in table_data.get("data", []):
        try:
            # Convert datetime strings back to datetime objects
            for key, value in row_data.items():
                if isinstance(value, str) and key == "date":
                    try:
                        row_data[key] = datetime.fromisoformat(value)
                    except Exception:
                        pass
            
            # Skip password field for security
            if "password" in row_data:
                del row_data["password"]
            
            # Create new row
            new_row = model_class(**row_data)
            db.session.add(new_row)
            stats["rows_imported"] += 1
            
        except Exception as e:
            stats["errors"].append(f"Error importing row in {table_name}: {str(e)}")
    
    db.session.commit()
    return stats


def import_from_json_file(filepath: str) -> dict:
    """
    Import database from a JSON file.
    Returns import statistics.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            export_data = json.load(f)
        
        return import_database(export_data)
    except Exception as e:
        return {
            "tables_imported": 0,
            "rows_imported": 0,
            "errors": [f"Import error: {str(e)}"]
        }
