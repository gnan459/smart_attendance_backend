#!/usr/bin/env python3
"""
Database Inspector: A utility to inspect the SQLite database for the Smart Attendance System
"""
import sqlite3
import os
import sys
from datetime import datetime
import argparse

def get_database_structure(db_path):
    """Get the structure of the database"""
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n===== DATABASE STRUCTURE =====")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("Columns:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, primary_key = col
            print(f"  - {col_name} ({col_type}){' PRIMARY KEY' if primary_key else ''}{' NOT NULL' if not_null else ''}")
    
    conn.close()

def get_table_data(db_path, table_name, limit=10):
    """Get data from a specific table"""
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if not cursor.fetchone():
        print(f"Table not found: {table_name}")
        conn.close()
        return
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    
    print(f"\n===== DATA FROM TABLE: {table_name} =====")
    if not rows:
        print("No data found in this table.")
    else:
        # Print column headers
        header = " | ".join(columns)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            values = []
            for col in columns:
                value = row[col]
                if value is None:
                    values.append("NULL")
                else:
                    values.append(str(value))
            print(" | ".join(values))
    
    # Get count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"\nTotal records: {count}")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Inspect the Smart Attendance System database')
    parser.add_argument('--db', default='smart_attendance.db', help='Path to the database file')
    parser.add_argument('--table', help='Show data from a specific table')
    parser.add_argument('--limit', type=int, default=10, help='Limit the number of records displayed')
    parser.add_argument('--structure', action='store_true', help='Show database structure')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db):
        print(f"Database file not found: {args.db}")
        print("Run the application first to create the database.")
        sys.exit(1)
    
    if args.structure or not args.table:
        get_database_structure(args.db)
    
    if args.table:
        get_table_data(args.db, args.table, args.limit)

if __name__ == "__main__":
    main()