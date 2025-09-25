import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
  RefreshControl,
} from 'react-native';
import {
  Text,
  Card,
  Button,
  Title,
  Paragraph,
  Chip,
  FAB,
  Portal,
  Modal,
  TextInput,
} from 'react-native-paper';
import ApiService from '../services/ApiService';

const TeacherDashboard = ({ navigation }) => {
  const [activeSession, setActiveSession] = useState(null);
  const [currentToken, setCurrentToken] = useState(null);
  const [analytics, setAnalytics] = useState([]);
  const [showStartModal, setShowStartModal] = useState(false);
  const [courseName, setCourseName] = useState('');
  const [classroom, setClassroom] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load analytics
      const analyticsData = await ApiService.getAttendanceAnalytics();
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleStartSession = async () => {
    if (!courseName || !classroom) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const sessionData = {
        course_name: courseName,
        classroom_location: classroom,
      };

      const session = await ApiService.startSession(sessionData);
      setActiveSession(session);
      
      // Get initial token
      const token = await ApiService.getCurrentToken(session.session_id);
      setCurrentToken(token);
      
      setShowStartModal(false);
      setCourseName('');
      setClassroom('');
      
      Alert.alert('Success', 'Class session started successfully!');
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start session');
    }
    setLoading(false);
  };

  const handleEndSession = async () => {
    if (!activeSession) return;

    Alert.alert(
      'End Session',
      'Are you sure you want to end this class session?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'End Session',
          style: 'destructive',
          onPress: async () => {
            try {
              await ApiService.endSession(activeSession.session_id);
              setActiveSession(null);
              setCurrentToken(null);
              Alert.alert('Success', 'Session ended successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to end session');
            }
          },
        },
      ]
    );
  };

  const refreshToken = async () => {
    if (!activeSession) return;
    
    try {
      const token = await ApiService.getCurrentToken(activeSession.session_id);
      setCurrentToken(token);
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh token');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    if (activeSession) {
      await refreshToken();
    }
    setRefreshing(false);
  };

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Active Session Card */}
        {activeSession ? (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Active Session</Title>
              <Paragraph>Course: {activeSession.course_name}</Paragraph>
              <Paragraph>Location: {activeSession.classroom_location}</Paragraph>
              <Paragraph>Started: {new Date(activeSession.start_time).toLocaleString()}</Paragraph>
              
              {currentToken && (
                <View style={styles.tokenContainer}>
                  <Text style={styles.tokenLabel}>Current BLE Token:</Text>
                  <Chip mode="outlined" style={styles.tokenChip}>
                    {currentToken.token_value}
                  </Chip>
                  <Button mode="outlined" onPress={refreshToken}>
                    Refresh Token
                  </Button>
                </View>
              )}
            </Card.Content>
            <Card.Actions>
              <Button mode="contained" onPress={handleEndSession}>
                End Session
              </Button>
            </Card.Actions>
          </Card>
        ) : (
          <Card style={styles.card}>
            <Card.Content>
              <Title>No Active Session</Title>
              <Paragraph>Start a new class session to begin attendance tracking</Paragraph>
            </Card.Content>
          </Card>
        )}

        {/* Analytics Card */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Attendance Analytics</Title>
            {analytics.length > 0 ? (
              analytics.map((student, index) => (
                <View key={index} style={styles.analyticsRow}>
                  <Text style={styles.studentName}>{student.student_name}</Text>
                  <Chip 
                    mode="outlined"
                    style={[
                      styles.percentageChip,
                      { backgroundColor: student.attendance_percentage > 75 ? '#e8f5e8' : '#ffeaea' }
                    ]}
                  >
                    {student.attendance_percentage}%
                  </Chip>
                </View>
              ))
            ) : (
              <Paragraph>No attendance data available</Paragraph>
            )}
          </Card.Content>
        </Card>
      </ScrollView>

      {/* FAB for starting session */}
      {!activeSession && (
        <FAB
          style={styles.fab}
          icon="plus"
          onPress={() => setShowStartModal(true)}
        />
      )}

      {/* Start Session Modal */}
      <Portal>
        <Modal
          visible={showStartModal}
          onDismiss={() => setShowStartModal(false)}
          contentContainerStyle={styles.modal}
        >
          <Title>Start New Session</Title>
          <TextInput
            label="Course Name"
            value={courseName}
            onChangeText={setCourseName}
            mode="outlined"
            style={styles.modalInput}
          />
          <TextInput
            label="Classroom Location"
            value={classroom}
            onChangeText={setClassroom}
            mode="outlined"
            style={styles.modalInput}
          />
          <View style={styles.modalActions}>
            <Button onPress={() => setShowStartModal(false)}>Cancel</Button>
            <Button
              mode="contained"
              onPress={handleStartSession}
              loading={loading}
            >
              Start Session
            </Button>
          </View>
        </Modal>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 15,
    marginBottom: 10,
  },
  tokenContainer: {
    marginTop: 15,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  tokenLabel: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  tokenChip: {
    marginBottom: 10,
  },
  analyticsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  studentName: {
    flex: 1,
    fontSize: 16,
  },
  percentageChip: {
    minWidth: 80,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
  modalInput: {
    marginBottom: 15,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
  },
});

export default TeacherDashboard;