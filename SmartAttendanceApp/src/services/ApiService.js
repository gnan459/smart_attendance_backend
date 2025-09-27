import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// const BASE_URL = 'http://10.0.2.2:8000/api/v1'; // Android emulator
const BASE_URL = 'http://192.168.1.7:8000/api/v1'; // Real device (use your IP)

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use(async (config) => {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Authentication endpoints
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await this.api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    if (response.data.access_token) {
      await AsyncStorage.setItem('authToken', response.data.access_token);
    }
    
    return response.data;
  }

  async register(userData) {
    const response = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async logout() {
    await AsyncStorage.removeItem('authToken');
  }

  // Teacher endpoints
  async startSession(sessionData) {
    const response = await this.api.post('/teacher/session/start', sessionData);
    return response.data;
  }

  async endSession(sessionId) {
    const response = await this.api.post(`/teacher/session/${sessionId}/end`);
    return response.data;
  }

  async getCurrentToken(sessionId) {
    const response = await this.api.get(`/teacher/session/${sessionId}/token`);
    return response.data;
  }

  async getAttendanceAnalytics(period = 'month') {
    const response = await this.api.get(`/teacher/analytics/attendance_percentage?period=${period}`);
    return response.data;
  }

  // Student endpoints
  async submitToken(tokenData) {
    const response = await this.api.post('/student/token/submit', tokenData);
    return response.data;
  }

  async verifyBiometric(biometricData) {
    const response = await this.api.post('/student/biometric/verify', biometricData);
    return response.data;
  }

  // Session endpoints
  async getSession(sessionId) {
    const response = await this.api.get(`/session/${sessionId}`);
    return response.data;
  }
}

export default new ApiService();