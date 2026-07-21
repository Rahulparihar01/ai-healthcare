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
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '', address: '', contact_email: '', contact_phone: '', license_number: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [hospRes, labRes, pharmRes] = await Promise.all([
        api.get('/hospitals/list'),
        api.get('/labs/list'),
        api.get('/pharmacies/list')
      ]);
      setHospitals(hospRes.data);
      setLabs(labRes.data);
      setPharmacies(pharmRes.data);
    } catch (error) {
      console.error("Failed to fetch data", error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (activeTab === 'hospitals') {
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
      setFormData({ name: '', address: '', contact_email: '', contact_phone: '', license_number: '' });
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
      </div>

      {/* Add Facility Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2rem', width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2>Register New {activeTab === 'hospitals' ? 'Hospital' : activeTab === 'labs' ? 'Laboratory' : 'Pharmacy'}</h2>
            <form onSubmit={handleRegister}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className="input-group">
                  <label className="input-label">Name</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, name: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Address</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, address: e.target.value})} />
                </div>
                {(activeTab === 'labs' || activeTab === 'pharmacies') && (
                  <div className="input-group">
                    <label className="input-label">License Number</label>
                    <input className="input-field" required onChange={e => setFormData({...formData, license_number: e.target.value})} />
                  </div>
                )}
                <div className="input-group">
                  <label className="input-label">Contact Email</label>
                  <input type="email" className="input-field" required onChange={e => setFormData({...formData, contact_email: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Contact Phone</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, contact_phone: e.target.value})} />
                </div>
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
