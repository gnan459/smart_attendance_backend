// Web Bluetooth API Implementation for Student Attendance
// This runs in the student's web browser

class BluetoothAttendanceScanner {
    constructor() {
        this.device = null;
        this.server = null;
        this.service = null;
        this.characteristic = null;
        
        // Your attendance system's BLE service UUID
        this.SERVICE_UUID = '12345678-1234-5678-9abc-123456789abc';
        this.TOKEN_CHARACTERISTIC_UUID = '87654321-4321-8765-cba9-987654321abc';
    }

    // Check if browser supports Web Bluetooth
    isBluetoothSupported() {
        return 'bluetooth' in navigator;
    }

    // Scan for teacher's BLE advertisement
    async scanForClassSession() {
        try {
            console.log('Scanning for class session...');
            
            // Request BLE device with your attendance service
            this.device = await navigator.bluetooth.requestDevice({
                filters: [{
                    services: [this.SERVICE_UUID]
                }],
                optionalServices: [this.SERVICE_UUID]
            });

            console.log('Found device:', this.device.name);
            
            // Connect to the device
            this.server = await this.device.gatt.connect();
            console.log('Connected to GATT server');
            
            // Get the attendance service
            this.service = await this.server.getPrimaryService(this.SERVICE_UUID);
            console.log('Got attendance service');
            
            // Get the token characteristic
            this.characteristic = await this.service.getCharacteristic(this.TOKEN_CHARACTERISTIC_UUID);
            console.log('Got token characteristic');
            
            return true;
            
        } catch (error) {
            console.error('Bluetooth scanning failed:', error);
            throw error;
        }
    }

    // Read current BLE token from teacher's device
    async getCurrentToken() {
        try {
            if (!this.characteristic) {
                throw new Error('Not connected to BLE device');
            }
            
            // Read the current token
            const value = await this.characteristic.readValue();
            const tokenData = new TextDecoder().decode(value);
            const tokenInfo = JSON.parse(tokenData);
            
            console.log('Received token data:', tokenInfo);
            
            return {
                sessionId: tokenInfo.session_id,
                token: tokenInfo.current_token,
                courseName: tokenInfo.course_name,
                classroom: tokenInfo.classroom,
                timestamp: new Date()
            };
            
        } catch (error) {
            console.error('Failed to read token:', error);
            throw error;
        }
    }

    // Submit attendance with BLE token
    async submitAttendance(studentToken) {
        try {
            // Get current BLE token
            const bleTokenData = await this.getCurrentToken();
            
            // Submit to your backend API
            const response = await fetch('/api/v1/student/token/submit', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${studentToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: bleTokenData.sessionId,
                    token_value: bleTokenData.token,
                    rssi: -50, // Can get actual RSSI in real implementation
                    timestamp: bleTokenData.timestamp.toISOString()
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('Attendance submitted successfully:', result);
                return result;
            } else {
                throw new Error(result.detail || 'Submission failed');
            }
            
        } catch (error) {
            console.error('Attendance submission failed:', error);
            throw error;
        }
    }

    // Disconnect from BLE device
    disconnect() {
        if (this.device && this.device.gatt.connected) {
            this.device.gatt.disconnect();
            console.log('Disconnected from BLE device');
        }
    }
}

// Usage example for students
async function markAttendanceWithBLE() {
    const scanner = new BluetoothAttendanceScanner();
    
    try {
        // Check browser support
        if (!scanner.isBluetoothSupported()) {
            alert('Your browser does not support Web Bluetooth');
            return;
        }
        
        // Scan for teacher's BLE advertisement
        console.log('Click to scan for class session...');
        await scanner.scanForClassSession();
        
        // Submit attendance
        const studentToken = 'your-jwt-token-here';
        const result = await scanner.submitAttendance(studentToken);
        
        console.log('Attendance marked:', result);
        
        // Proceed with biometric verification
        // ... biometric verification code here
        
    } catch (error) {
        console.error('BLE attendance failed:', error);
        alert('Failed to mark attendance: ' + error.message);
    } finally {
        scanner.disconnect();
    }
}

// Expose to global scope
window.BluetoothAttendanceScanner = BluetoothAttendanceScanner;
window.markAttendanceWithBLE = markAttendanceWithBLE;