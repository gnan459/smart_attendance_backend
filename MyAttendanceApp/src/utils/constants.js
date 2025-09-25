export const API_CONFIG = {
  // BASE_URL: 'http://10.0.2.2:8000/api/v1', // Android emulator
  BASE_URL: 'http://192.168.1.7:8000/api/v1', // Real device
  TIMEOUT: 10000,
};

export const BLE_CONFIG = {
  SERVICE_UUID: '9f3c1e70-12ab-4c8d-9c77-7a3fba5b91d2', // Attendance Service
  TOKEN_CHARACTERISTIC_UUID: '4b7f2a6d-45c2-4f19-b8f4-3ea83ad91b56', // Token Characteristic
  SCAN_TIMEOUT: 30000, // 30 seconds
};

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'authToken',
  USER_TYPE: 'userType',
  USER_DATA: 'userData',
};

export const USER_TYPES = {
  TEACHER: 'teacher',
  STUDENT: 'student',
};