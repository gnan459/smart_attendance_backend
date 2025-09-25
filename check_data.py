#!/usr/bin/env python3
"""
Quick script to check current database data
"""
import sqlite3

def check_data():
    conn = sqlite3.connect('smart_attendance.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=== CURRENT DATABASE DATA ===\n")
    
    # Check users
    print("USERS:")
    cursor.execute("SELECT id, email, full_name, is_teacher FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"  ID: {user['id']}, Email: {user['email']}, Name: {user['full_name']}, Teacher: {user['is_teacher']}")
    else:
        print("  No users found")
    
    print("\nCLASS SESSIONS:")
    cursor.execute("SELECT id, session_id, teacher_id, course_name, classroom_location, is_active, start_time FROM class_sessions")
    sessions = cursor.fetchall()
    if sessions:
        for session in sessions:
            print(f"  ID: {session['id']}, Session: {session['session_id'][:8]}..., Teacher: {session['teacher_id']}")
            print(f"    Course: {session['course_name']}, Location: {session['classroom_location']}, Active: {session['is_active']}")
            print(f"    Started: {session['start_time']}")
    else:
        print("  No sessions found")
    
    print("\nBLE TOKENS:")
    cursor.execute("SELECT id, session_id, token_value, is_active, created_at FROM ble_tokens")
    tokens = cursor.fetchall()
    if tokens:
        for token in tokens:
            print(f"  ID: {token['id']}, Session: {token['session_id']}, Token: {token['token_value'][:15]}..., Active: {token['is_active']}")
    else:
        print("  No tokens found")
    
    print("\nATTENDANCE RECORDS:")
    cursor.execute("SELECT COUNT(*) as count FROM attendance_records")
    count = cursor.fetchone()['count']
    print(f"  Total records: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_data()