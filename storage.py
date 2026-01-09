"""
Storage Module
SQLite-based persistence for summaries.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'summaries.db')


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            original_text TEXT,
            summary TEXT,
            key_points TEXT,
            mode TEXT,
            length TEXT,
            file_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def save_summary(
    filename: str,
    original_text: str,
    summary: str,
    key_points: List[str],
    mode: str,
    length: str,
    file_type: str
) -> int:
    """
    Save a summary to the database.
    
    Returns:
        ID of the saved summary
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO summaries (filename, original_text, summary, key_points, mode, length, file_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, original_text, summary, json.dumps(key_points), mode, length, file_type))
    
    summary_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return summary_id


def get_summary(summary_id: int) -> Optional[Dict]:
    """
    Get a specific summary by ID.
    
    Returns:
        Summary dictionary or None if not found
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM summaries WHERE id = ?', (summary_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict_from_row(row)
    return None


def list_summaries(limit: int = 50) -> List[Dict]:
    """
    List all saved summaries.
    
    Returns:
        List of summary dictionaries (without full text for brevity)
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, mode, length, file_type, created_at,
               substr(summary, 1, 200) as summary_preview
        FROM summaries
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_summary(summary_id: int) -> bool:
    """
    Delete a summary by ID.
    
    Returns:
        True if deleted, False if not found
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM summaries WHERE id = ?', (summary_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def dict_from_row(row) -> Dict:
    """Convert a database row to a dictionary."""
    data = dict(row)
    if 'key_points' in data and data['key_points']:
        try:
            data['key_points'] = json.loads(data['key_points'])
        except json.JSONDecodeError:
            data['key_points'] = []
    return data


def export_summary(summary_id: int, format: str = 'txt') -> Optional[str]:
    """
    Export a summary in the specified format.
    
    Args:
        summary_id: ID of the summary
        format: 'txt' or 'json'
        
    Returns:
        Formatted string or None if not found
    """
    summary = get_summary(summary_id)
    if not summary:
        return None
    
    if format == 'json':
        return json.dumps(summary, indent=2, default=str)
    
    # Plain text format
    lines = [
        f"Document: {summary['filename']}",
        f"Date: {summary['created_at']}",
        f"Mode: {summary['mode']} | Length: {summary['length']}",
        "",
        "=" * 50,
        "SUMMARY",
        "=" * 50,
        summary['summary'],
        "",
        "=" * 50,
        "KEY POINTS",
        "=" * 50,
    ]
    
    for i, point in enumerate(summary.get('key_points', []), 1):
        lines.append(f"{i}. {point}")
    
    return '\n'.join(lines)
