import { BleManager, Device, Service, Characteristic } from 'react-native-ble-plx';
import { PermissionsAndroid, Platform } from 'react-native';

class BLEService {
  constructor() {
    this.manager = new BleManager();
    this.connectedDevice = null;
    
    // Your attendance system BLE service UUID
    this.SERVICE_UUID = '9f3c1e70-12ab-4c8d-9c77-7a3fba5b91d2';
    this.TOKEN_CHARACTERISTIC_UUID = '4b7f2a6d-45c2-4f19-b8f4-3ea83ad91b56';
  }

  async requestPermissions() {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.requestMultiple([
        PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
        PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
      ]);
      
      return Object.values(granted).every(
        permission => permission === PermissionsAndroid.RESULTS.GRANTED
      );
    }
    return true;
  }

  async startScanning(onDeviceFound) {
    const hasPermissions = await this.requestPermissions();
    if (!hasPermissions) {
      throw new Error('Bluetooth permissions not granted');
    }

    const state = await this.manager.state();
    if (state !== 'PoweredOn') {
      throw new Error('Bluetooth is not enabled');
    }

    console.log('Starting BLE scan...');
    
    this.manager.startDeviceScan(
      [this.SERVICE_UUID], 
      { allowDuplicates: false },
      (error, device) => {
        if (error) {
          console.error('BLE scan error:', error);
          return;
        }

        if (device && device.name && device.name.includes('Class-')) {
          console.log('Found class device:', device.name);
          onDeviceFound(device);
        }
      }
    );
  }

  stopScanning() {
    this.manager.stopDeviceScan();
    console.log('Stopped BLE scanning');
  }

  async connectToDevice(device) {
    try {
      console.log('Connecting to device:', device.name);
      
      this.connectedDevice = await device.connect();
      await this.connectedDevice.discoverAllServicesAndCharacteristics();
      
      console.log('Connected and discovered services');
      return true;
      
    } catch (error) {
      console.error('Connection failed:', error);
      throw error;
    }
  }

  async readCurrentToken() {
    if (!this.connectedDevice) {
      throw new Error('No device connected');
    }

    try {
      const characteristic = await this.connectedDevice.readCharacteristicForService(
        this.SERVICE_UUID,
        this.TOKEN_CHARACTERISTIC_UUID
      );

      const tokenData = JSON.parse(characteristic.value);
      console.log('Read token data:', tokenData);
      
      return {
        sessionId: tokenData.session_id,
        token: tokenData.current_token,
        courseName: tokenData.course_name,
        classroom: tokenData.classroom,
        rssi: this.connectedDevice.rssi || -50,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('Failed to read token:', error);
      throw error;
    }
  }

  disconnect() {
    if (this.connectedDevice) {
      this.connectedDevice.cancelConnection();
      this.connectedDevice = null;
      console.log('Disconnected from BLE device');
    }
  }

  // For testing without actual BLE hardware
//   async simulateBLEScan() {
//     return new Promise((resolve) => {
//       setTimeout(() => {
//         resolve({
//           sessionId: 'd607f0d8-d737-4a32-bd11-7b66f7c9474b',
//           token: 'simulated_ble_token_123',
//           courseName: 'ML-Class',
//           classroom: 'B4-104',
//           rssi: -45,
//           timestamp: new Date().toISOString()
//         });
//       }, 2000);
//     });
//   }

}


export default new BLEService();