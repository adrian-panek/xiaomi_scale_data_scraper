"""Database operations for storing measurements."""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any
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


def get_all_measurements(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Get all measurements from the database, ordered by timestamp descending."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, weight, impedance, bmi, bmr, body_fat_percentage
            FROM measurements
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "weight": row["weight"],
                "impedance": row["impedance"],
                "bmi": row["bmi"],
                "bmr": row["bmr"],
                "body_fat_percentage": row["body_fat_percentage"]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"❌ Error retrieving measurements: {e}")
        return []


def get_recent_measurements(limit: int = 10, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Get recent measurements from the database, ordered by timestamp descending."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, weight, impedance, bmi, bmr, body_fat_percentage
            FROM measurements
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "weight": row["weight"],
                "impedance": row["impedance"],
                "bmi": row["bmi"],
                "bmr": row["bmr"],
                "body_fat_percentage": row["body_fat_percentage"]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"❌ Error retrieving recent measurements: {e}")
        return []

