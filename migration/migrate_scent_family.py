"""
Migration script to add scent_family and fragrance_notes columns to soaps table.
Run this on production to add the new columns.
"""
import sqlite3
from contextlib import contextmanager


@contextmanager
def get_db_connection(db_path: str):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    finally:
        conn.close()


def migrate(db_path: str = "instance/storage.db") -> None:
    """
    Add scent_family and fragrance_notes columns to soaps table.

    Args:
        db_path: Path to the SQLite database file
    """
    print(f"Connecting to database: {db_path}")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Check if 'soaps' table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='soaps'
        """)
        if not cursor.fetchone():
            print("Error: 'soaps' table does not exist. Nothing to migrate.")
            return

        # Check which columns already exist
        cursor.execute("PRAGMA table_info(soaps)")
        columns = [row['name'] for row in cursor.fetchall()]

        migrated = []

        if 'scent_family' not in columns:
            print("Adding 'scent_family' column to 'soaps' table...")
            cursor.execute(
                "ALTER TABLE soaps ADD COLUMN scent_family VARCHAR(100)"
            )
            migrated.append("scent_family")

        if 'fragrance_notes' not in columns:
            print("Adding 'fragrance_notes' column to 'soaps' table...")
            cursor.execute(
                "ALTER TABLE soaps ADD COLUMN fragrance_notes VARCHAR(200)"
            )
            migrated.append("fragrance_notes")

        if not migrated:
            print("All columns already exist. Nothing to do.")
            return

        conn.commit()
        print(f"Migration complete! Added: {', '.join(migrated)}")


if __name__ == "__main__":
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/storage.db"

    print("=" * 50)
    print("Soaps Scent Family Migration")
    print("Add scent_family + fragrance_notes columns")
    print("=" * 50)
    print()

    migrate(db_path)
