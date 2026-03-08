"""
CRUD Helpers

Utility functions for model operations and conversions.
"""

import os
from app import app, db
from app.models import *
from app.utils import split_file_path


def get_model_class(table_name: str):
    """Get model class from table name using SQLAlchemy's registry."""
    # Try to get from SQLAlchemy's model registry
    for mapper in db.Model.registry.mappers:
        if mapper.class_.__tablename__ == table_name:
            return mapper.class_
    
    # Fallback for known tables (if registry doesn't have them yet)
    table_to_class = {
        "images": Image,
        "soaps": Soap,
        "does": Doe,
        "foundation": Foundation,
        "goats": Goat,
        "inquiries": Inquiry,
        "books_hs": BookHS,
        "books_st": BookST,
        "users": User,
        "adoptions": Adoption,
    }
    
    return table_to_class.get(table_name)


def column_is_nullable(table_name: str, column_name: str) -> bool:
    """Check if a column is nullable using SQLAlchemy metadata."""
    try:
        model_class = get_model_class(table_name)
        if model_class:
            return getattr(model_class, column_name).nullable
        
        # Fallback to metadata inspection
        metadata = db.MetaData()
        metadata.reflect(bind=db.engine)
        
        if table_name in metadata.tables:
            table_obj = metadata.tables[table_name]
            if column_name in table_obj.columns:
                return table_obj.columns[column_name].nullable
    except Exception:
        pass
    
    return True  # Default to nullable for safety


def image_id_from_string(id_string: str) -> int:
    """
    Convert image ID string to integer.
    Handles both numeric IDs and file paths.
    """
    try:
        image_id = int(id_string)
        if not Image.query.get(image_id):
            raise IndexError(f"The image with ID ({image_id}) doesn't exist")
    except ValueError:
        directory, filename = split_file_path(id_string)
        image = Image.query.filter_by(filename=filename, directory=directory).first()

        if not image:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], directory, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file '{os.path.join(directory, filename)}' was not found")
            
            image = Image(filename=filename, directory=directory)
            db.session.add(image)
            db.session.commit()

        image_id = image.id

    return image_id


def goat_id_from_string(id_string: str) -> int:
    """
    Convert goat ID string to integer.
    Handles both numeric IDs and goat names (creates goat if doesn't exist).
    """
    try:
        goat_id = int(id_string)
        if not Goat.query.get(goat_id):
            raise IndexError(f"The goat with ID ({goat_id}) doesn't exist")
    except ValueError:
        goat = Goat.query.filter_by(name=id_string).first()

        if not goat:
            goat = Goat(name=id_string)
            db.session.add(goat)
            db.session.commit()

        goat_id = goat.id

    return goat_id
