"""Database operations for storing measurements."""

import sqlite3
from datetime import datetime
from config import DB_PATH


def init_database(db_path: str = DB_PATH):
    """Initialize the SQLite database and create measurements table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            weight REAL NOT NULL,
            impedance INTEGER NOT NULL,
            bmi REAL NOT NULL,
            bmr REAL NOT NULL,
            body_fat_percentage REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON measurements(timestamp)
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {db_path}")


def store_measurement(weight: float, impedance: int, bmi: float, bmr: float, 
                     body_fat: float, db_path: str = DB_PATH) -> bool:
    """Store a single measurement in the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO measurements 
            (timestamp, weight, impedance, bmi, bmr, body_fat_percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), weight, impedance, bmi, bmr, body_fat))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error storing measurement: {e}")
        return False

