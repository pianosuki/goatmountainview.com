"""
Admin Panel Field Mappings

Defines user-friendly field configurations for all database tables.
Used by both routes.py and jinja.py for consistent form rendering.
"""

# Field mappings for add/edit forms (routes.py)
USER_FIELDS = {
    "soaps": [
        {"name": "name", "type": "text"},
        {"name": "ingredients", "type": "text"},
        {"name": "weight", "type": "number"},
        {"name": "image", "type": "image"},
    ],
    "does": [
        {"name": "name", "type": "text"},
        {"name": "description", "type": "text"},
        {"name": "link", "type": "url"},
        {"name": "image", "type": "image"},
    ],
    "foundation": [
        {"name": "name", "type": "text"},
        {"name": "description", "type": "text"},
        {"name": "link", "type": "url"},
        {"name": "image", "type": "image"},
    ],
    "adoptions": [
        {"name": "name", "type": "text"},
        {"name": "description", "type": "text"},
        {"name": "image", "type": "image"},
    ],
    "books_hs": [
        {"name": "name", "type": "text"},
        {"name": "editors", "type": "text"},
        {"name": "year", "type": "number"},
        {"name": "link", "type": "url"},
    ],
    "books_st": [
        {"name": "name", "type": "text"},
        {"name": "editors", "type": "text"},
        {"name": "year", "type": "number"},
        {"name": "link", "type": "url"},
    ],
    "inquiries": [
        {"name": "first_name", "type": "text"},
        {"name": "last_name", "type": "text"},
        {"name": "email", "type": "text"},
        {"name": "comment", "type": "text"},
    ],
    "users": [
        {"name": "username", "type": "text"},
        {"name": "password", "type": "password"},
    ],
    "images": [
        {"name": "directory", "type": "text"},
        {"name": "note", "type": "text"},
    ],
}

# Field mappings for display forms (jinja.py) - includes labels and requirements
DISPLAY_FIELDS = {
    "soaps": [
        {"name": "name", "label": "Soap Name", "type": "text", "required": True},
        {"name": "ingredients", "label": "Ingredients", "type": "textarea", "required": True},
        {"name": "weight", "label": "Weight (oz)", "type": "number", "required": True},
        {"name": "image", "label": "Photo", "type": "image", "required": False},
    ],
    "does": [
        {"name": "name", "label": "Goat Name", "type": "text", "required": True},
        {"name": "description", "label": "Description", "type": "textarea", "required": True},
        {"name": "link", "label": "Pedigree Link (optional)", "type": "url", "required": False},
        {"name": "image", "label": "Photo", "type": "image", "required": False},
    ],
    "foundation": [
        {"name": "name", "label": "Goat Name", "type": "text", "required": True},
        {"name": "description", "label": "Description", "type": "textarea", "required": True},
        {"name": "link", "label": "Pedigree Link (optional)", "type": "url", "required": False},
        {"name": "image", "label": "Photo", "type": "image", "required": False},
    ],
    "adoptions": [
        {"name": "name", "label": "Goat Name", "type": "text", "required": True},
        {"name": "description", "label": "Description", "type": "textarea", "required": True},
        {"name": "image", "label": "Photo", "type": "image", "required": False},
    ],
    "books_hs": [
        {"name": "name", "label": "Book Title", "type": "text", "required": True},
        {"name": "editors", "label": "Editors", "type": "text", "required": True},
        {"name": "year", "label": "Year", "type": "number", "required": True},
        {"name": "link", "label": "Link", "type": "url", "required": True},
    ],
    "books_st": [
        {"name": "name", "label": "Book Title", "type": "text", "required": True},
        {"name": "editors", "label": "Editors", "type": "text", "required": True},
        {"name": "year", "label": "Year", "type": "number", "required": True},
        {"name": "link", "label": "Link", "type": "url", "required": True},
    ],
    "inquiries": [
        {"name": "first_name", "label": "First Name", "type": "text", "required": True},
        {"name": "last_name", "label": "Last Name", "type": "text", "required": True},
        {"name": "email", "label": "Email", "type": "text", "required": True},
        {"name": "comment", "label": "Message", "type": "textarea", "required": True},
    ],
    "users": [
        {"name": "username", "label": "Username", "type": "text", "required": True},
        {"name": "password", "label": "Password", "type": "password", "required": False},
    ],
    "images": [
        {"name": "directory", "label": "Folder (optional)", "type": "text", "required": False},
        {"name": "note", "label": "Note (optional)", "type": "textarea", "required": False},
    ],
}

# Display columns for table views
DISPLAY_COLUMNS = {
    "soaps": ["name", "weight", "image"],
    "does": ["name", "description", "image"],
    "foundation": ["name", "description", "image"],
    "adoptions": ["name", "description", "image"],
    "books_hs": ["name", "editors", "year"],
    "books_st": ["name", "editors", "year"],
    "inquiries": ["first_name", "last_name", "email", "date"],
    "users": ["username"],
    "images": ["thumbnail", "filename", "directory", "note"],
}
