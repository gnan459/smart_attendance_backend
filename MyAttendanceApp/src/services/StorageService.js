import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../utils/constants';

class StorageService {
  async setItem(key, value) {
    try {
      const jsonValue = JSON.stringify(value);
      await AsyncStorage.setItem(key, jsonValue);
    } catch (error) {
      console.error('Storage setItem error:', error);
    }
  }

  async getItem(key) {
    try {
      const jsonValue = await AsyncStorage.getItem(key);
      return jsonValue != null ? JSON.parse(jsonValue) : null;
    } catch (error) {
      console.error('Storage getItem error:', error);
      return null;
    }
  }

  async removeItem(key) {
    try {
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Storage removeItem error:', error);
    }
  }

  async clear() {
    try {
      await AsyncStorage.clear();
    } catch (error) {
      console.error('Storage clear error:', error);
    }
  }

  // Auth-specific methods
  async setAuthToken(token) {
    await this.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
  }

  async getAuthToken() {
    return await this.getItem(STORAGE_KEYS.AUTH_TOKEN);
  }

  async setUserData(userData) {
    await this.setItem(STORAGE_KEYS.USER_DATA, userData);
  }

  async getUserData() {
    return await this.getItem(STORAGE_KEYS.USER_DATA);
  }

  async logout() {
    await this.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    await this.removeItem(STORAGE_KEYS.USER_DATA);
  }
}

export default new StorageService();