import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Building2, Users, FlaskConical, Pill, Plus, MoreHorizontal } from 'lucide-react';
import api from '../api';

export default function SuperAdminDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('hospitals');
  const [hospitals, setHospitals] = useState([]);
  const [labs, setLabs] = useState([]);
  const [pharmacies, setPharmacies] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '', address: '', contact_email: '', contact_phone: '', license_number: '',
    username: '', password: '', email: '', role: 'Hospital Admin', hospital_id: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [hospRes, labRes, pharmRes, auditRes] = await Promise.all([
        api.get('/hospitals/list'),
        api.get('/labs/list'),
        api.get('/pharmacies/list'),
        api.get('/identity/audit/logs/all')
      ]);
      setHospitals(hospRes.data);
      setLabs(labRes.data);
      setPharmacies(pharmRes.data);
      setAuditLogs(auditRes.data);
    } catch (error) {
      console.error("Failed to fetch data", error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (activeTab === 'users') {
        if (!formData.hospital_id) {
          alert("Please select a hospital for the staff member.");
          setLoading(false);
          return;
        }
        await api.post('/identity/auth/register', { 
          username: formData.username, 
          password: formData.password, 
          email: formData.email, 
          role: formData.role,
          hospital_id: parseInt(formData.hospital_id)
        });
        alert("Staff registered successfully!");
      } else if (activeTab === 'hospitals') {
        await api.post('/hospitals/create', formData);
        alert("Hospital registered successfully!");
      } else if (activeTab === 'labs') {
        await api.post('/labs/create', formData);
        alert("Laboratory registered successfully!");
      } else if (activeTab === 'pharmacies') {
        await api.post('/pharmacies/create', formData);
        alert("Pharmacy registered successfully!");
      }
      setShowAddModal(false);
      setFormData({ 
        name: '', address: '', contact_email: '', contact_phone: '', license_number: '',
        username: '', password: '', email: '', role: 'Hospital Admin', hospital_id: ''
      });
      fetchData();
    } catch (error) {
      alert("Error registering: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Shield color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Super Admin</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          System Master,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div className={`nav-item ${activeTab === 'hospitals' ? 'active' : ''}`} onClick={() => setActiveTab('hospitals')}>
            <Building2 size={20} />
            Hospitals
          </div>
          <div className={`nav-item ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
            <Users size={20} />
            System Users
          </div>
          <div className={`nav-item ${activeTab === 'labs' ? 'active' : ''}`} onClick={() => setActiveTab('labs')}>
            <FlaskConical size={20} />
            Laboratories
          </div>
          <div className={`nav-item ${activeTab === 'pharmacies' ? 'active' : ''}`} onClick={() => setActiveTab('pharmacies')}>
            <Pill size={20} />
            Pharmacies
          </div>
          <div className={`nav-item ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>
            <Shield size={20} />
            Audit Logs
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        {activeTab === 'hospitals' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Hospital Network
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Manage registered hospitals and clinics across the platform.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                <Plus size={18} /> Register Hospital
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Hospital Name</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Address</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Contact</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {hospitals.map(hosp => (
                    <tr key={hosp.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>#{hosp.id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{hosp.name}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{hosp.address}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{hosp.contact_phone}</td>
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

        {activeTab === 'users' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  System Users
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Register administrative staff and assign them to hospitals.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                <Plus size={18} /> Register Staff
              </button>
            </div>
            
            <div className="glass-panel" style={{ background: 'white', padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Click "Register Staff" to create a new Hospital Admin or Receptionist.
            </div>
          </>
        )}

        {(activeTab === 'labs' || activeTab === 'pharmacies') && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  {activeTab === 'labs' ? 'Laboratories' : 'Pharmacies'}
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Manage registered {activeTab === 'labs' ? 'laboratories' : 'pharmacies'} in the network.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                <Plus size={18} /> Register {activeTab === 'labs' ? 'Lab' : 'Pharmacy'}
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Name</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>License No.</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Contact</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(activeTab === 'labs' ? labs : pharmacies).map(facility => (
                    <tr key={facility.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>#{facility.id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{facility.name}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{facility.license_number}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{facility.contact_phone}</td>
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

        {activeTab === 'audit' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  System Audit Logs
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  View a real-time ledger of system access and actions.
                </p>
              </div>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Timestamp</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Action</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Status</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>IP Address</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map(log => (
                    <tr key={log.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>
                        {log.action}
                      </td>
                      <td style={{ padding: '1rem 1.5rem' }}>
                        <span style={{ 
                          color: log.status === 'SUCCESS' ? 'green' : 'red', 
                          fontWeight: 'bold', 
                          background: log.status === 'SUCCESS' ? '#e6ffe6' : '#ffe6e6', 
                          padding: '0.25rem 0.5rem', 
                          borderRadius: '4px' 
                        }}>
                          {log.status}
                        </span>
                      </td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{log.ip_address || 'N/A'}</td>
                    </tr>
                  ))}
                  {auditLogs.length === 0 && (
                    <tr>
                      <td colSpan="4" style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-tertiary)' }}>No audit logs found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Add Facility Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2rem', width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2>Register New {activeTab === 'hospitals' ? 'Hospital' : activeTab === 'labs' ? 'Laboratory' : activeTab === 'pharmacies' ? 'Pharmacy' : 'Staff'}</h2>
            <form onSubmit={handleRegister}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {activeTab === 'users' ? (
                  <>
                    <div className="input-group">
                      <label className="input-label">Username</label>
                      <input className="input-field" required value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Email</label>
                      <input type="email" className="input-field" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Password</label>
                      <input type="password" className="input-field" required value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Role</label>
                      <select className="input-field" required value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})}>
                        <option value="Hospital Admin">Hospital Admin</option>
                        <option value="Receptionist">Receptionist</option>
                      </select>
                    </div>
                    <div className="input-group">
                      <label className="input-label">Assign Hospital</label>
                      <select className="input-field" required value={formData.hospital_id} onChange={e => setFormData({...formData, hospital_id: e.target.value})}>
                        <option value="">Select a hospital...</option>
                        {hospitals.map(h => (
                          <option key={h.id} value={h.id}>{h.name}</option>
                        ))}
                      </select>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="input-group">
                      <label className="input-label">Name</label>
                      <input className="input-field" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Address</label>
                      <input className="input-field" required value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
                    </div>
                    {(activeTab === 'labs' || activeTab === 'pharmacies') && (
                      <div className="input-group">
                        <label className="input-label">License Number</label>
                        <input className="input-field" required value={formData.license_number} onChange={e => setFormData({...formData, license_number: e.target.value})} />
                      </div>
                    )}
                    <div className="input-group">
                      <label className="input-label">Contact Email</label>
                      <input type="email" className="input-field" required value={formData.contact_email} onChange={e => setFormData({...formData, contact_email: e.target.value})} />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Contact Phone</label>
                      <input className="input-field" required value={formData.contact_phone} onChange={e => setFormData({...formData, contact_phone: e.target.value})} />
                    </div>
                  </>
                )}
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={loading}>
                  {loading ? 'Registering...' : 'Register'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
