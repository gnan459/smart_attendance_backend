import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Text,
  Card,
  Button,
  Title,
  Paragraph,
  ActivityIndicator,
  Chip,
  ProgressBar,
} from 'react-native-paper';
import ApiService from '../services/ApiService';
import BLEService from '../services/BLEService';

const StudentDashboard = ({ navigation }) => {
  const [scanning, setScanning] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [foundDevices, setFoundDevices] = useState([]);
  const [currentStep, setCurrentStep] = useState(1); // 1: Scan, 2: Submit, 3: Verify, 4: Complete
  const [tokenData, setTokenData] = useState(null);
  const [attendanceResult, setAttendanceResult] = useState(null);

  const resetAttendanceFlow = () => {
    setCurrentStep(1);
    setTokenData(null);
    setAttendanceResult(null);
    setFoundDevices([]);
  };

  const startBLEScan = async () => {
    setScanning(true);
    setFoundDevices([]);
    
    try {
      // For demo, use simulated BLE scan
      const simulatedData = await BLEService.simulateBLEScan();
      setTokenData(simulatedData);
      setCurrentStep(2);
      
      /* For real BLE implementation:
      await BLEService.startScanning((device) => {
        setFoundDevices(prev => [...prev, device]);
      });
      */
      
    } catch (error) {
      Alert.alert('Error', error.message);
    }
    setScanning(false);
  };

  const stopScanning = () => {
    BLEService.stopScanning();
    setScanning(false);
  };

  const connectToClass = async (device) => {
    setConnecting(true);
    try {
      await BLEService.connectToDevice(device);
      const tokenData = await BLEService.readCurrentToken();
      setTokenData(tokenData);
      setCurrentStep(2);
      stopScanning();
    } catch (error) {
      Alert.alert('Error', 'Failed to connect to class session');
    }
    setConnecting(false);
  };

  const submitAttendanceToken = async () => {
    if (!tokenData) return;
    
    setSubmitting(true);
    try {
      const submissionData = {
        session_id: tokenData.sessionId,
        token_value: tokenData.token,
      };
      
      const result = await ApiService.submitToken(submissionData);
      console.log('Token submission result:', result);
      
      if (result.status === 'success') {
        setCurrentStep(3);
      } else {
        Alert.alert('Error', result.message || 'Token submission failed');
      }
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit token');
    }
    setSubmitting(false);
  };

  const verifyBiometric = async () => {
    if (!tokenData) return;
    
    setVerifying(true);
    try {
      const biometricData = {
        session_id: tokenData.sessionId,
        biometric_data: `fingerprint_${Date.now()}`, // Simulated biometric data
      };
      
      const result = await ApiService.verifyBiometric(biometricData);
      console.log('Biometric verification result:', result);
      
      setAttendanceResult(result);
      setCurrentStep(4);
      
      if (result.final_status === 'present') {
        Alert.alert('Success', 'Attendance marked successfully!');
      } else {
        Alert.alert('Warning', `Attendance status: ${result.final_status}`);
      }
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Biometric verification failed');
    }
    setVerifying(false);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Step 1: Scan for Class</Title>
              <Paragraph>
                Look for your teacher's BLE broadcast to join the class session.
              </Paragraph>
              
              {scanning && (
                <View style={styles.scanningContainer}>
                  <ActivityIndicator size="large" />
                  <Text style={styles.scanningText}>Scanning for classes...</Text>
                </View>
              )}
              
              {foundDevices.map((device, index) => (
                <Card key={index} style={styles.deviceCard}>
                  <Card.Content>
                    <Text style={styles.deviceName}>{device.name}</Text>
                    <Text style={styles.deviceId}>RSSI: {device.rssi}</Text>
                  </Card.Content>
                  <Card.Actions>
                    <Button 
                      onPress={() => connectToClass(device)}
                      loading={connecting}
                    >
                      Join Class
                    </Button>
                  </Card.Actions>
                </Card>
              ))}
            </Card.Content>
            <Card.Actions>
              <Button 
                mode="contained" 
                onPress={startBLEScan}
                loading={scanning}
                disabled={scanning}
              >
                {scanning ? 'Scanning...' : 'Start Scan'}
              </Button>
              {scanning && (
                <Button onPress={stopScanning}>
                  Stop Scan
                </Button>
              )}
            </Card.Actions>
          </Card>
        );

      case 2:
        return (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Step 2: Submit Attendance Token</Title>
              <Paragraph>
                Found class session! Submit your attendance token.
              </Paragraph>
              
              {tokenData && (
                <View style={styles.sessionInfo}>
                  <Text style={styles.sessionLabel}>Course: {tokenData.courseName}</Text>
                  <Text style={styles.sessionLabel}>Location: {tokenData.classroom}</Text>
                  <Text style={styles.sessionLabel}>Signal: {tokenData.rssi} dBm</Text>
                  
                  <View style={styles.tokenContainer}>
                    <Text style={styles.tokenLabel}>BLE Token:</Text>
                    <Chip mode="outlined">{tokenData.token}</Chip>
                  </View>
                </View>
              )}
            </Card.Content>
            <Card.Actions>
              <Button onPress={resetAttendanceFlow}>Back</Button>
              <Button 
                mode="contained"
                onPress={submitAttendanceToken}
                loading={submitting}
              >
                Submit Token
              </Button>
            </Card.Actions>
          </Card>
        );

      case 3:
        return (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Step 3: Biometric Verification</Title>
              <Paragraph>
                Token submitted successfully! Complete biometric verification to finalize attendance.
              </Paragraph>
              
              <View style={styles.biometricContainer}>
                <Text style={styles.biometricText}>
                  Place your finger on the sensor or provide biometric data
                </Text>
              </View>
            </Card.Content>
            <Card.Actions>
              <Button onPress={resetAttendanceFlow}>Back</Button>
              <Button 
                mode="contained"
                onPress={verifyBiometric}
                loading={verifying}
              >
                Verify Biometric
              </Button>
            </Card.Actions>
          </Card>
        );

      case 4:
        return (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Attendance Complete!</Title>
              
              {attendanceResult && (
                <View style={styles.resultContainer}>
                  <Chip 
                    mode="flat"
                    style={[
                      styles.statusChip,
                      { 
                        backgroundColor: attendanceResult.final_status === 'present' 
                          ? '#e8f5e8' 
                          : '#ffeaea' 
                      }
                    ]}
                  >
                    Status: {attendanceResult.final_status.toUpperCase()}
                  </Chip>
                  
                  <Text style={styles.resultText}>
                    Biometric Verified: {attendanceResult.verified ? 'Yes' : 'No'}
                  </Text>
                  <Text style={styles.resultText}>
                    Token Count: {attendanceResult.token_count}
                  </Text>
                </View>
              )}
            </Card.Content>
            <Card.Actions>
              <Button 
                mode="contained" 
                onPress={resetAttendanceFlow}
              >
                Mark Another Attendance
              </Button>
            </Card.Actions>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView>
        {/* Progress indicator */}
        <Card style={styles.progressCard}>
          <Card.Content>
            <Text style={styles.progressTitle}>Attendance Progress</Text>
            <ProgressBar 
              progress={currentStep / 4} 
              style={styles.progressBar}
            />
            <Text style={styles.progressText}>
              Step {currentStep} of 4: {
                ['Scan for Class', 'Submit Token', 'Verify Biometric', 'Complete'][currentStep - 1]
              }
            </Text>
          </Card.Content>
        </Card>

        {renderStepContent()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  progressCard: {
    margin: 15,
    marginBottom: 10,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    marginBottom: 5,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
  },
  card: {
    margin: 15,
    marginTop: 10,
  },
  scanningContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  scanningText: {
    marginTop: 10,
    fontSize: 16,
  },
  deviceCard: {
    marginTop: 10,
    backgroundColor: '#f9f9f9',
  },
  deviceName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  deviceId: {
    fontSize: 14,
    color: '#666',
  },
  sessionInfo: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  sessionLabel: {
    fontSize: 16,
    marginBottom: 5,
  },
  tokenContainer: {
    marginTop: 10,
  },
  tokenLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  biometricContainer: {
    alignItems: 'center',
    paddingVertical: 30,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    marginTop: 15,
  },
  biometricText: {
    fontSize: 16,
    textAlign: 'center',
    color: '#666',
  },
  resultContainer: {
    marginTop: 15,
    alignItems: 'center',
  },
  statusChip: {
    marginBottom: 15,
    paddingHorizontal: 20,
  },
  resultText: {
    fontSize: 16,
    marginBottom: 5,
  },
});

export default StudentDashboard;