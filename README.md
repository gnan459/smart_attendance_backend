# Smart Attendance System Backend

A FastAPI backend for a Smart Attendance System using BLE tokens and biometric verification.

## Features

- **Bluetooth Low Energy (BLE) Tokens**: Secure tokens for proximity-based attendance tracking
- **Biometric Verification**: Attendance validation through biometric data
- **Automatic Token Rotation**: Tokens change every 5 minutes to prevent cheating
- **Teacher and Student Interfaces**: Separate APIs for different user roles

- **Analytics & Insights**: Teacher dashboards for:
   - Student attendance percentage (monthly/semester)
   - Daily class present/absent counts
   - Attendance trends over time (visualization-ready)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gnan459/smart_attendance_backend.git
cd smart_attendance_backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

Start the development server:
```bash
python run.py
```

The API will be available at http://localhost:8000 and the documentation at http://localhost:8000/api/v1/docs

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/token` - Login and get access token

### Teacher Endpoints
- `POST /api/v1/teacher/session/start` - Start a new class session
- `POST /api/v1/teacher/session/{session_id}/end` - End a class session
- `GET /api/v1/teacher/session/{session_id}/token` - Get current BLE token for advertising
- `GET /api/v1/teacher/analytics/attendance_percentage` - Get each student’s attendance percentage for the current month/semester
- `GET /api/v1/teacher/analytics/daily_class_report` - Get total present vs absent count per class for a given day
- `GET /api/v1/teacher/analytics/attendance_trends` - Get attendance trends over time (daily counts for charting)


### Student Endpoints
- `POST /api/v1/student/token/submit` - Submit a captured BLE token
- `POST /api/v1/student/biometric/verify` - Submit biometric data for verification


## Workflow

1. **Class Start**:
   - Teacher logs in and starts a class session
   - System generates a unique session ID and BLE token
   - Teacher's device advertises the token via BLE

2. **During Class**:
   - System generates a new token every 5 minutes
   - Students capture tokens and upload to the server
   - Server tracks continuous presence

3. **Class End**:
   - Teacher ends the class session
   - Students perform final biometric verification
   - System validates attendance based on token submissions and biometric verification

## Mobile App Integration

The mobile apps (teacher and student) should integrate with this backend by:

1. **Teacher App**:
   - Authenticating with the backend
   - Creating/ending class sessions
   - Receiving and broadcasting BLE tokens

2. **Student App**:
   - Authenticating with the backend
   - Scanning for and capturing BLE tokens
   - Submitting tokens to the server
   - Providing biometric data for verification