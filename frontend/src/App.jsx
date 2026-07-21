import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import DoctorDashboard from './components/DoctorDashboard';
import Register from './components/Register';
import VerifyOTP from './components/VerifyOTP';
import SuperAdminDashboard from './components/SuperAdminDashboard';
import HospitalAdminDashboard from './components/HospitalAdminDashboard';
import ReceptionistDashboard from './components/ReceptionistDashboard';
import PatientDashboard from './components/PatientDashboard';
import './index.css';

// A simple wrapper to protect routes
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <div className="app-container" style={{justifyContent: 'center', alignItems: 'center'}}>
      <div className="glass-panel" style={{padding: '2rem'}}>
        <h2>Access Denied</h2>
        <p>You do not have permission to view this page.</p>
      </div>
    </div>;
  }
  
  return children;
};

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard/doctor" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard/doctor" replace /> : <Register />} />
      <Route path="/verify-otp" element={user ? <Navigate to="/dashboard/doctor" replace /> : <VerifyOTP />} />
      
      {/* Protected Routes */}
      <Route 
        path="/dashboard/doctor" 
        element={
          <ProtectedRoute allowedRoles={['Doctor', 'Super Admin']}>
            <DoctorDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/super-admin" 
        element={
          <ProtectedRoute allowedRoles={['Super Admin']}>
            <SuperAdminDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/hospital-admin" 
        element={
          <ProtectedRoute allowedRoles={['Hospital Admin', 'Super Admin']}>
            <HospitalAdminDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/receptionist" 
        element={
          <ProtectedRoute allowedRoles={['Receptionist', 'Super Admin']}>
            <ReceptionistDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/patient" 
        element={
          <ProtectedRoute allowedRoles={['Patient']}>
            <PatientDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Default Redirect */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
