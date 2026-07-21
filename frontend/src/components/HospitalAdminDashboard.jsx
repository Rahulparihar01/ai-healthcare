import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Building2, Stethoscope, Plus, Search, MoreHorizontal, Settings } from 'lucide-react';
import api from '../api';

export default function HospitalAdminDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('doctors');
  const [doctors, setDoctors] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    username: '', password: '', email: '', phone_number: '',
    department: '', specialization: '', license_number: '', medical_council: ''
  });

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      // In a real app, we would fetch doctors for this specific hospital ID
      // Hardcoded hospital_id 1 for demo purposes
      const res = await api.get('/doctors/list?hospital_id=1');
      setDoctors(res.data);
    } catch (error) {
      console.error("Failed to fetch doctors", error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Hardcoded hospital_id 1 for demo purposes
      await api.post('/doctors/register', { ...formData, hospital_id: 1 });
      alert("Doctor registered successfully!");
      setShowAddModal(false);
      fetchDoctors();
    } catch (error) {
      alert("Error registering doctor: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Building2 color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>HealthID Admin</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div className={`nav-item ${activeTab === 'doctors' ? 'active' : ''}`} onClick={() => setActiveTab('doctors')}>
            <Stethoscope size={20} />
            Manage Doctors
          </div>
          <div className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
            <Settings size={20} />
            Hospital Settings
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        {activeTab === 'doctors' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Doctor Management
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Register and manage hospital faculty members.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                <Plus size={18} /> Register Doctor
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Name</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Department</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Specialization</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>License</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map(doc => (
                    <tr key={doc.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{doc.user?.username}</td>
                      <td style={{ padding: '1rem 1.5rem' }}>{doc.department}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{doc.specialization}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{doc.license_number}</td>
                      <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                        <button className="btn btn-secondary" style={{ padding: '0.4rem' }}><MoreHorizontal size={18} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Add Doctor Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2rem', width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2>Register New Doctor</h2>
            <form onSubmit={handleRegister}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="input-group">
                  <label className="input-label">Username</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, username: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Email</label>
                  <input type="email" className="input-field" required onChange={e => setFormData({...formData, email: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Password</label>
                  <input type="password" className="input-field" required onChange={e => setFormData({...formData, password: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Phone</label>
                  <input className="input-field" onChange={e => setFormData({...formData, phone_number: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Department</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, department: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Specialization</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, specialization: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">License Number</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, license_number: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Medical Council</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, medical_council: e.target.value})} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={loading}>
                  {loading ? 'Registering...' : 'Complete Registration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
