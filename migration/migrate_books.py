"""
Migration script to move data from 'books' table to 'books_st' table.
Run this on production to migrate existing Science & Technology books.
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


def migrate_books(db_path: str = "instance/goatmountainview.db") -> None:
    """
    Migrate all books from 'books' table to 'books_st' table.
    
    Args:
        db_path: Path to the SQLite database file
    """
    print(f"Connecting to database: {db_path}")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if 'books' table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='books'
        """)
        if not cursor.fetchone():
            print("Error: 'books' table does not exist. Nothing to migrate.")
            return
        
        # Check if 'books_st' table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='books_st'
        """)
        if not cursor.fetchone():
            print("Error: 'books_st' table does not exist. Please run setup() first to create the table.")
            return
        
        # Count existing records in books_st
        cursor.execute("SELECT COUNT(*) FROM books_st")
        existing_count = cursor.fetchone()[0]
        print(f"Existing records in books_st: {existing_count}")
        
        # Get all books from the old table
        cursor.execute("SELECT id, name, editors, year, link FROM books")
        books = cursor.fetchall()
        
        if not books:
            print("No books found in 'books' table. Nothing to migrate.")
            return
        
        print(f"Found {len(books)} books to migrate from 'books' table.")
        
        # Insert books into books_st (skip duplicates based on name)
        migrated_count = 0
        skipped_count = 0
        
        for book in books:
            try:
                # Check if book with same name already exists in books_st
                cursor.execute("SELECT id FROM books_st WHERE name = ?", (book['name'],))
                if cursor.fetchone():
                    print(f"  Skipping (duplicate): {book['name']}")
                    skipped_count += 1
                    continue
                
                cursor.execute("""
                    INSERT INTO books_st (name, editors, year, link)
                    VALUES (?, ?, ?, ?)
                """, (book['name'], book['editors'], book['year'], book['link']))
                print(f"  Migrated: {book['name']} ({book['year']})")
                migrated_count += 1
                
            except sqlite3.IntegrityError as e:
                print(f"  Error migrating '{book['name']}': {e}")
                skipped_count += 1
        
        # Commit the transaction
        conn.commit()
        
        print("\n" + "=" * 50)
        print(f"Migration complete!")
        print(f"  Migrated: {migrated_count} books")
        print(f"  Skipped:  {skipped_count} books (duplicates)")
        print(f"  Total in books_st: {existing_count + migrated_count}")
        print("=" * 50)
        
        # Ask for confirmation before dropping old table
        response = input("\nDo you want to drop the old 'books' table? (y/N): ").strip().lower()
        if response == 'y':
            cursor.execute("DROP TABLE books")
            conn.commit()
            print("Dropped 'books' table.")
        else:
            print("Kept 'books' table. You can drop it manually later if needed.")


if __name__ == "__main__":
    import sys
    
    # Allow custom database path as command line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/storage.db"
    
    print("=" * 50)
    print("Books Table Migration Script")
    print("books -> books_st")
    print("=" * 50)
    print()
    
    migrate_books(db_path)
