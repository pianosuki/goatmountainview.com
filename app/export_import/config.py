"""
Export/Import Configuration

Shared configuration for database export and import operations.
"""

# Tables to export/import (in order to respect foreign keys)
# Note: "users" is intentionally excluded for security (passwords)
EXPORT_IMPORT_TABLES = [
    "images",
    "goats",
    "soaps",
    "does",
    "foundation",
    "adoptions",
    "books_hs",
    "books_st",
    "inquiries"
]
