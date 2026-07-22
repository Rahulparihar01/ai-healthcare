import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, FileText, QrCode, Activity, Heart, ShieldAlert, Edit2 } from 'lucide-react';
import api from '../api';
import Timeline from './Timeline';

export default function PatientDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  // Onboarding state
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [formData, setFormData] = useState({
    blood_group: '', emergency_contact_name: '', emergency_contact_phone: '', allergies: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/patients/profile');
      setProfile(res.data);
      setNeedsOnboarding(false);
    } catch (error) {
      if (error.response?.status === 404) {
        setNeedsOnboarding(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updateData = {
        blood_group: formData.blood_group,
        emergency_contact_name: formData.emergency_contact_name,
        emergency_contact_phone: formData.emergency_contact_phone,
        allergies: formData.allergies ? formData.allergies.split(',').map(a => a.trim()) : []
      };
      
      const res = await api.put(`/patients/${profile.health_id}`, updateData);
      setProfile(res.data);
      setShowEditModal(false);
      alert("Profile updated successfully!");
    } catch (error) {
      alert("Error updating profile: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading...</div>;
  }

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Heart color="var(--accent-emerald)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>My HealthID</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
            <User size={20} />
            My Profile
          </div>
          <div className={`nav-item ${activeTab === 'records' ? 'active' : ''}`} onClick={() => setActiveTab('records')}>
            <FileText size={20} />
            Medical Records
          </div>
          <div className={`nav-item ${activeTab === 'vitals' ? 'active' : ''}`} onClick={() => setActiveTab('vitals')}>
            <Activity size={20} />
            Vitals History
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        
        {needsOnboarding ? (
          <div className="glass-panel" style={{ background: 'white', padding: '3rem', maxWidth: '600px', margin: '0 auto', borderRadius: '16px' }}>
            <h2 style={{ marginBottom: '1rem', color: '#000' }}>Complete Your Profile</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Please provide some basic medical information to generate your Health ID.</p>
            <form onSubmit={handleOnboard}>
               <div className="input-group">
                  <label className="input-label">Blood Group</label>
                  <input className="input-field" placeholder="e.g. O+" onChange={e => setFormData({...formData, blood_group: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Emergency Contact Name</label>
                  <input className="input-field" onChange={e => setFormData({...formData, emergency_contact_name: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Emergency Contact Phone</label>
                  <input className="input-field" onChange={e => setFormData({...formData, emergency_contact_phone: e.target.value})} />
                </div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>Generate Health ID</button>
            </form>
          </div>
        ) : profile && activeTab === 'profile' ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Patient Dashboard
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Your official Health ID and complete medical profile.
                </p>
              </div>
              <button className="btn btn-secondary" onClick={() => {
                setFormData({
                  blood_group: profile.blood_group || '',
                  emergency_contact_name: profile.emergency_contact_name || '',
                  emergency_contact_phone: profile.emergency_contact_phone || '',
                  allergies: profile.allergies ? profile.allergies.join(', ') : ''
                });
                setShowEditModal(true);
              }}>
                <Edit2 size={18} /> Edit Details
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem' }}>
              
              {/* Left Column: QR and ID */}
              <div>
                <div className="glass-panel" style={{ background: 'white', padding: '2rem', textAlign: 'center', borderRadius: '16px', marginBottom: '1.5rem' }}>
                  <img src={`http://localhost:8000/${profile.qr_code_path}`} alt="Health ID QR" style={{ width: '200px', height: '200px', marginBottom: '1.5rem' }} />
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>
                    Health ID
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#000', letterSpacing: '0.05em' }}>
                    {profile.health_id}
                  </div>
                </div>

                {profile.allergies?.length > 0 && (
                  <div className="glass-panel" style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '1.5rem', borderRadius: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#dc2626', fontWeight: 600, marginBottom: '0.5rem' }}>
                      <ShieldAlert size={20} /> Allergies
                    </div>
                    <ul style={{ color: '#991b1b', margin: 0, paddingLeft: '1.5rem', fontSize: '0.95rem' }}>
                      {profile.allergies.map((a, i) => <li key={i}>{a}</li>)}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Column: Details */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div className="glass-panel" style={{ background: 'white', padding: '2rem', borderRadius: '16px' }}>
                  <h3 style={{ fontSize: '1.1rem', color: '#000', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
                    Emergency Information
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Blood Group</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 500, color: '#000' }}>{profile.blood_group || 'Not specified'}</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>Emergency Contact</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 500, color: '#000' }}>{profile.emergency_contact_name || 'Not specified'}</div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem' }}>{profile.emergency_contact_phone}</div>
                    </div>
                  </div>
                </div>

                <div className="glass-panel" style={{ background: 'white', padding: '2rem', borderRadius: '16px' }}>
                  <h3 style={{ fontSize: '1.1rem', color: '#000', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
                    Medical History
                  </h3>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                    {Object.keys(profile.medical_history || {}).length > 0 ? (
                      <pre style={{ fontFamily: 'inherit', whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(profile.medical_history, null, 2)}
                      </pre>
                    ) : (
                      'No significant medical history recorded.'
                    )}
                  </div>
                </div>
              </div>

            </div>
          </>
        ) : profile && activeTab === 'records' ? (
           <Timeline healthId={profile.health_id} />
        ) : (
           <div style={{ color: 'var(--text-secondary)' }}>Section under construction.</div>
        )}
      </div>

      {/* Edit Profile Modal */}
      {showEditModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2.5rem', width: '500px', maxHeight: '90vh', overflowY: 'auto', borderRadius: '16px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#000' }}>Edit Medical Details</h2>
            <form onSubmit={handleEdit}>
              <div className="input-group">
                <label className="input-label">Blood Group</label>
                <input className="input-field" value={formData.blood_group} onChange={e => setFormData({...formData, blood_group: e.target.value})} />
              </div>
              <div className="input-group">
                <label className="input-label">Emergency Contact Name</label>
                <input className="input-field" value={formData.emergency_contact_name} onChange={e => setFormData({...formData, emergency_contact_name: e.target.value})} />
              </div>
              <div className="input-group">
                <label className="input-label">Emergency Contact Phone</label>
                <input className="input-field" value={formData.emergency_contact_phone} onChange={e => setFormData({...formData, emergency_contact_phone: e.target.value})} />
              </div>
              <div className="input-group">
                <label className="input-label">Allergies (comma separated)</label>
                <textarea className="input-field" value={formData.allergies} onChange={e => setFormData({...formData, allergies: e.target.value})} rows={3}></textarea>
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowEditModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1, background: 'var(--accent-blue)' }} disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
