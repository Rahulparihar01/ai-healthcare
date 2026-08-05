import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import Login from './components/Login';
import DoctorDashboard from './components/DoctorDashboard';
import Register from './components/Register';
import VerifyOTP from './components/VerifyOTP';
import SuperAdminDashboard from './components/SuperAdminDashboard';
import HospitalAdminDashboard from './components/HospitalAdminDashboard';
import ReceptionistDashboard from './components/ReceptionistDashboard';
import PatientDashboard from './components/PatientDashboard';
import LabTechnicianDashboard from './components/LabTechnicianDashboard';
import OfflineIndicator from './components/OfflineIndicator';
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

const getDashboardRoute = (role) => {
  switch (role) {
    case 'Super Admin': return '/dashboard/super-admin';
    case 'Hospital Admin': return '/dashboard/hospital-admin';
    case 'Receptionist': return '/dashboard/receptionist';
    case 'Patient': return '/dashboard/patient';
    case 'Lab Technician': return '/dashboard/lab-technician';
    default: return '/dashboard/doctor';
  }
};

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={getDashboardRoute(user.role)} replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to={getDashboardRoute(user.role)} replace /> : <Register />} />
      <Route path="/verify-otp" element={user ? <Navigate to={getDashboardRoute(user.role)} replace /> : <VerifyOTP />} />
      
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
      <Route 
        path="/dashboard/lab-technician" 
        element={
          <ProtectedRoute allowedRoles={['Lab Technician', 'Super Admin']}>
            <LabTechnicianDashboard />
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
        <OfflineIndicator />
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}



export default App;
