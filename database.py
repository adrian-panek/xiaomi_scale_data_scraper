"""Database operations for storing measurements."""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

def init_database():
    """Initialize the PostgreSQL database and create measurements table if it doesn't exist."""
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
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
    
    connection.commit()
    connection.close()
    print(f"✅ Database initialized: {DB_NAME}")


def store_measurement(weight: float, impedance: int, bmi: float, bmr: float, 
                     body_fat: float) -> bool:
    """Store a single measurement in the database."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            INSERT INTO measurements 
            (timestamp, weight, impedance, bmi, bmr, body_fat_percentage)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (datetime.now(), weight, impedance, bmi, bmr, body_fat))
        
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Error storing measurement: {e}")
        return False


def get_all_measurements() -> List[Dict[str, Any]]:
    """Get all measurements from the database, ordered by timestamp descending."""
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, timestamp, weight, impedance, bmi, bmr, body_fat_percentage
            FROM measurements
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        connection.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ Error retrieving measurements: {e}")
        return []


def get_recent_measurements(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent measurements from the database, ordered by timestamp descending."""
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, timestamp, weight, impedance, bmi, bmr, body_fat_percentage
            FROM measurements
            ORDER BY timestamp DESC
            LIMIT %s
        ''', (limit,))
        
        rows = cursor.fetchall()
        connection.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ Error retrieving recent measurements: {e}")
        return []

