"""
Database module for Flight Incognito search history
"""

import sqlite3
from datetime import date, datetime
from typing import List, Dict, Optional
from contextlib import contextmanager


DB_NAME = "flight_searches.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                depart_date TEXT NOT NULL,
                return_date TEXT,
                trip_type TEXT NOT NULL,
                adults INTEGER DEFAULT 1,
                children INTEGER DEFAULT 0,
                infants INTEGER DEFAULT 0,
                cabin TEXT DEFAULT 'Economy',
                search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_timestamp 
            ON search_history(search_timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_route 
            ON search_history(origin, destination)
        """)


def save_search(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: Optional[date],
    trip_type: str,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy"
) -> int:
    """
    Save a search to the database
    Returns: search_id
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO search_history 
            (origin, destination, depart_date, return_date, trip_type, 
             adults, children, infants, cabin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            origin.upper().strip(),
            destination.upper().strip(),
            depart_date.isoformat(),
            return_date.isoformat() if return_date else None,
            trip_type,
            adults,
            children,
            infants,
            cabin
        ))
        
        return cursor.lastrowid


def get_recent_searches(limit: int = 10) -> List[Dict]:
    """Get recent searches ordered by timestamp"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM search_history
            ORDER BY search_timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_popular_routes(limit: int = 5) -> List[Dict]:
    """Get most frequently searched routes"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                origin,
                destination,
                COUNT(*) as search_count,
                MAX(search_timestamp) as last_searched
            FROM search_history
            GROUP BY origin, destination
            ORDER BY search_count DESC, last_searched DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_search_by_id(search_id: int) -> Optional[Dict]:
    """Get a specific search by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM search_history
            WHERE id = ?
        """, (search_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_search(search_id: int) -> bool:
    """Delete a search by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM search_history
            WHERE id = ?
        """, (search_id,))
        
        return cursor.rowcount > 0


def clear_all_history() -> int:
    """Clear all search history. Returns number of deleted records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM search_history")
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM search_history")
        
        return count


def get_total_searches() -> int:
    """Get total number of searches in history"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM search_history")
        return cursor.fetchone()[0]
