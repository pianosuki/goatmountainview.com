"""
Migration script to add scent_family column to soaps table.
Run this on production to add the new column.
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
    Add scent_family column to soaps table.

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

        # Check if column already exists
        cursor.execute("PRAGMA table_info(soaps)")
        columns = [row['name'] for row in cursor.fetchall()]

        if 'scent_family' in columns:
            print("Column 'scent_family' already exists. Nothing to do.")
            return

        print("Adding 'scent_family' column to 'soaps' table...")
        cursor.execute(
            "ALTER TABLE soaps ADD COLUMN scent_family VARCHAR(200)"
        )
        conn.commit()
        print("Migration complete!")


if __name__ == "__main__":
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/storage.db"

    print("=" * 50)
    print("Soaps Scent Family Migration")
    print("Add scent_family column to soaps table")
    print("=" * 50)
    print()

    migrate(db_path)
