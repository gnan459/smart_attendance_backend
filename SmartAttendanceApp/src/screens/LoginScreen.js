import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Card,
  Title,
  Paragraph,
  RadioButton,
  ActivityIndicator,
} from 'react-native-paper';
import ApiService from '../services/ApiService';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isTeacher, setIsTeacher] = useState('false');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        // Login
        await ApiService.login(email, password);
        const userType = isTeacher === 'true' ? 'teacher' : 'student';
        navigation.replace(userType === 'teacher' ? 'TeacherDashboard' : 'StudentDashboard');
      } else {
        // Register
        const userData = {
          email,
          password,
          full_name: email.split('@')[0], // Simple name from email
          is_teacher: isTeacher === 'true',
        };
        
        await ApiService.register(userData);
        Alert.alert('Success', 'Registration successful! Please login.');
        setIsLogin(true);
      }
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Authentication failed');
    }
    setLoading(false);
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Smart Attendance</Title>
          <Paragraph style={styles.subtitle}>
            {isLogin ? 'Login to continue' : 'Create new account'}
          </Paragraph>

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
          />

          {!isLogin && (
            <View style={styles.radioContainer}>
              <Text style={styles.radioLabel}>Account Type:</Text>
              <RadioButton.Group
                onValueChange={setIsTeacher}
                value={isTeacher}
              >
                <View style={styles.radioOption}>
                  <RadioButton value="true" />
                  <Text>Teacher</Text>
                </View>
                <View style={styles.radioOption}>
                  <RadioButton value="false" />
                  <Text>Student</Text>
                </View>
              </RadioButton.Group>
            </View>
          )}

          <Button
            mode="contained"
            onPress={handleAuth}
            loading={loading}
            disabled={loading}
            style={styles.button}
          >
            {isLogin ? 'Login' : 'Register'}
          </Button>

          <Button
            mode="text"
            onPress={() => setIsLogin(!isLogin)}
            style={styles.switchButton}
          >
            {isLogin ? 'Need an account? Register' : 'Already have account? Login'}
          </Button>
        </Card.Content>
      </Card>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  card: {
    padding: 20,
  },
  title: {
    textAlign: 'center',
    marginBottom: 10,
    fontSize: 28,
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 30,
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 20,
    paddingVertical: 8,
  },
  switchButton: {
    marginTop: 10,
  },
  radioContainer: {
    marginBottom: 20,
  },
  radioLabel: {
    fontSize: 16,
    marginBottom: 10,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
});

export default LoginScreen;