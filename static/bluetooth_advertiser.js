// Teacher's BLE Advertisement Simulator
// This runs on teacher's computer/phone to broadcast BLE signals

class BluetoothAttendanceAdvertiser {
    constructor(sessionData) {
        this.sessionData = sessionData;
        this.isAdvertising = false;
        this.advertisementInterval = null;
        
        this.SERVICE_UUID = '12345678-1234-5678-9abc-123456789abc';
        this.TOKEN_CHARACTERISTIC_UUID = '87654321-4321-8765-cba9-987654321abc';
    }

    // Start advertising BLE signals (using Web Bluetooth Peripheral API)
    async startAdvertising() {
        try {
            // Check if browser supports BLE advertising
            if (!('bluetooth' in navigator) || !navigator.bluetooth.advertise) {
                // Fallback: Use service worker or WebRTC for peer-to-peer
                this.startSoftwareAdvertising();
                return;
            }

            // Real BLE advertising (if supported)
            await navigator.bluetooth.advertise({
                advertisingData: {
                    localName: `Class-${this.sessionData.course_name}`,
                    serviceUuids: [this.SERVICE_UUID],
                    serviceData: {
                        [this.SERVICE_UUID]: this.encodeSessionData()
                    }
                },
                scanResponseData: {
                    completeLocalName: `${this.sessionData.course_name} - ${this.sessionData.classroom}`
                }
            });

            this.isAdvertising = true;
            console.log('Started BLE advertising for:', this.sessionData.course_name);
            
            // Start token rotation
            this.startTokenRotation();
            
        } catch (error) {
            console.error('BLE advertising failed:', error);
            // Fallback to software simulation
            this.startSoftwareAdvertising();
        }
    }

    // Software-based advertising simulation
    startSoftwareAdvertising() {
        console.log('Starting software BLE simulation...');
        
        // Create a virtual BLE service that students can "discover"
        this.createVirtualBLEService();
        this.isAdvertising = true;
        this.startTokenRotation();
        
        console.log('Software BLE advertising started for:', this.sessionData.course_name);
    }

    // Create virtual BLE service for testing
    createVirtualBLEService() {
        // Store BLE service data in localStorage for student apps to discover
        const virtualBLEData = {
            serviceUuid: this.SERVICE_UUID,
            deviceName: `Class-${this.sessionData.course_name}`,
            sessionData: this.sessionData,
            lastUpdated: Date.now()
        };
        
        localStorage.setItem('virtual_ble_service', JSON.stringify(virtualBLEData));
        
        // Broadcast to other tabs/windows (for same-device testing)
        const broadcastChannel = new BroadcastChannel('ble_attendance');
        broadcastChannel.postMessage({
            type: 'ble_advertisement',
            data: virtualBLEData
        });
    }

    // Encode session data for BLE transmission
    encodeSessionData() {
        const data = {
            session_id: this.sessionData.session_id,
            course_name: this.sessionData.course_name,
            classroom: this.sessionData.classroom_location,
            current_token: this.generateCurrentToken(),
            timestamp: Date.now()
        };
        
        return new TextEncoder().encode(JSON.stringify(data));
    }

    // Generate time-based rotating token
    generateCurrentToken() {
        const currentTimeSlot = Math.floor(Date.now() / (30 * 60 * 1000)); // 30-minute slots
        const tokenData = `${this.sessionData.session_id}:${currentTimeSlot}`;
        
        // Simple hash function (use crypto.subtle.digest in production)
        let hash = 0;
        for (let i = 0; i < tokenData.length; i++) {
            const char = tokenData.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        
        return hash.toString(16).substr(0, 16); // 16-character hex token
    }

    // Start automatic token rotation
    startTokenRotation() {
        // Update token every minute (to show rotation)
        this.advertisementInterval = setInterval(() => {
            if (this.isAdvertising) {
                this.updateAdvertisement();
            }
        }, 60000); // Update every minute
    }

    // Update BLE advertisement with new token
    updateAdvertisement() {
        console.log('Rotating BLE token...');
        
        // Update virtual BLE service
        this.createVirtualBLEService();
        
        const newToken = this.generateCurrentToken();
        console.log('New BLE token:', newToken);
        
        // Notify connected students
        const broadcastChannel = new BroadcastChannel('ble_attendance');
        broadcastChannel.postMessage({
            type: 'token_rotation',
            token: newToken,
            session_id: this.sessionData.session_id
        });
    }

    // Stop advertising
    stopAdvertising() {
        this.isAdvertising = false;
        
        if (this.advertisementInterval) {
            clearInterval(this.advertisementInterval);
            this.advertisementInterval = null;
        }
        
        // Clean up virtual BLE service
        localStorage.removeItem('virtual_ble_service');
        
        console.log('Stopped BLE advertising');
    }
}

// Usage for teachers
async function startClassBLEAdvertising(sessionData) {
    const advertiser = new BluetoothAttendanceAdvertiser(sessionData);
    
    try {
        await advertiser.startAdvertising();
        
        // Store advertiser reference for cleanup
        window.currentBLEAdvertiser = advertiser;
        
        return advertiser;
        
    } catch (error) {
        console.error('Failed to start BLE advertising:', error);
        throw error;
    }
}

// Stop advertising when class ends
function stopClassBLEAdvertising() {
    if (window.currentBLEAdvertiser) {
        window.currentBLEAdvertiser.stopAdvertising();
        window.currentBLEAdvertiser = null;
    }
}

// Expose to global scope
window.BluetoothAttendanceAdvertiser = BluetoothAttendanceAdvertiser;
window.startClassBLEAdvertising = startClassBLEAdvertising;
window.stopClassBLEAdvertising = stopClassBLEAdvertising;