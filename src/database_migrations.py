"""
Database migration helper
Safely adds new columns to existing tables
"""
import sqlite3


def migrate_add_stock_metrics(db_path='trades.db'):
    """Add stock metrics columns to trades table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(trades)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    # Columns to add
    new_columns = {
        'float': 'REAL DEFAULT NULL',
        'avg_volume': 'REAL DEFAULT NULL',
        'day_volume': 'REAL DEFAULT NULL',
        'market_cap': 'REAL DEFAULT NULL',
        'stock_type': 'TEXT DEFAULT NULL',
        'exchange': 'TEXT DEFAULT NULL',
        'auto_sector': 'TEXT DEFAULT NULL',
        'data_fetched': 'INTEGER DEFAULT 0'
    }

    # Add missing columns
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE trades ADD COLUMN {col_name} {col_type}')
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Column {col_name} might already exist: {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == '__main__':
    migrate_add_stock_metrics()