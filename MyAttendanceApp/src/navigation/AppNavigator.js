import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/LoginScreen';
import TeacherDashboard from '../screens/TeacherDashboard';
import StudentDashboard from '../screens/StudentDashboard';

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="TeacherDashboard" 
          component={TeacherDashboard}
          options={{ 
            title: 'Teacher Dashboard',
            headerLeft: null, // Disable back button
          }}
        />
        <Stack.Screen 
          name="StudentDashboard" 
          component={StudentDashboard}
          options={{ 
            title: 'Student Dashboard',
            headerLeft: null, // Disable back button
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;