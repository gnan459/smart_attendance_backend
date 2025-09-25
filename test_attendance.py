#!/usr/bin/env python3
"""
Quick attendance test script
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEACHER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU4NzgxOTQxfQ.MP3NUyYYauduZGJssRgThi0m_AFRtYXcXASgS_C_lbc"
STUDENT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzU4NzgyODY3fQ.RW-U5Z9FRIe71ypeMO8IfN1zz59be870xqD6vRDfKkc"
SESSION_ID = "d607f0d8-d737-4a32-bd11-7b66f7c9474b"

def test_attendance_flow():
    print("🎯 Testing Complete Attendance Flow")
    print("=" * 50)
    
    # Step 1: Get fresh BLE token as teacher
    print("\n1️⃣ Getting fresh BLE token (as teacher)...")
    teacher_headers = {"Authorization": f"Bearer {TEACHER_TOKEN}"}
    
    try:
        response = requests.get(f"{BASE_URL}/teacher/session/{SESSION_ID}/token", headers=teacher_headers)
        response.raise_for_status()
        token_data = response.json()
        ble_token = token_data["token_value"]
        print(f"✅ Got BLE token: {ble_token}")
    except Exception as e:
        print(f"❌ Failed to get token: {e}")
        return
    
    # Step 2: Submit token as student
    print("\n2️⃣ Submitting BLE token (as student)...")
    student_headers = {
        "Authorization": f"Bearer {STUDENT_TOKEN}",
        "Content-Type": "application/json"
    }
    submit_data = {
        "session_id": SESSION_ID,
        "token_value": ble_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/student/token/submit", 
                               headers=student_headers, 
                               json=submit_data)
        response.raise_for_status()
        submit_result = response.json()
        print(f"✅ Token submitted: {submit_result}")
    except Exception as e:
        print(f"❌ Token submission failed: {e}")
        if response.status_code == 400:
            print(f"Response: {response.text}")
        return
    
    # Step 3: Complete biometric verification
    print("\n3️⃣ Completing biometric verification...")
    biometric_data = {
        "session_id": SESSION_ID,
        "biometric_data": "sample_fingerprint_data_12345"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/student/biometric/verify",
                               headers=student_headers,
                               json=biometric_data)
        response.raise_for_status()
        biometric_result = response.json()
        print(f"✅ Biometric verified: {biometric_result}")
    except Exception as e:
        print(f"❌ Biometric verification failed: {e}")
        if response.status_code == 400:
            print(f"Response: {response.text}")
        return
    
    print(f"\n🎉 Attendance process completed successfully!")
    print(f"Final status: {biometric_result.get('final_status', 'unknown')}")

if __name__ == "__main__":
    test_attendance_flow()