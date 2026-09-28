import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Building2, Stethoscope, Plus, Search, MoreHorizontal, Settings, BarChart3, UserCheck, X } from 'lucide-react';
import api from '../api';
import PopulationDashboard from './analytics/PopulationDashboard';

const DEPARTMENT_SPECIALIZATIONS = {
  'General Medicine': ['Internal Medicine', 'Family Physician', 'General Practitioner', 'Geriatric Medicine'],
  'Cardiology': ['Interventional Cardiology', 'Clinical Cardiology', 'Pediatric Cardiology', 'Electrophysiology', 'Heart Failure Specialist'],
  'Neurology': ['General Neurology', 'Stroke Specialist', 'Epileptology', 'Neurocritical Care'],
  'Orthopedics': ['Orthopedic Surgery', 'Joint Replacement', 'Sports Medicine', 'Spine Specialist'],
  'Pediatrics': ['General Pediatrics', 'Neonatology', 'Pediatric Critical Care'],
  'Dermatology': ['Clinical Dermatology', 'Cosmetic Dermatology', 'Dermatopathology'],
  'Oncology': ['Medical Oncology', 'Surgical Oncology', 'Radiation Oncology'],
  'Radiology': ['Diagnostic Radiology', 'Interventional Radiology', 'Neuroradiology'],
  'Gynecology & Obstetrics': ['Obstetrics & Gynecology', 'Maternal-Fetal Medicine', 'Gynecologic Oncology'],
  'Emergency Medicine': ['Trauma Care', 'Emergency Physician', 'Resuscitation Specialist'],
  'ENT (Otolaryngology)': ['General ENT', 'Head & Neck Surgery', 'Rhinology & Sinus'],
  'Ophthalmology': ['Comprehensive Ophthalmology', 'Retina Specialist', 'Cataract & Glaucoma'],
  'Gastroenterology': ['Clinical Gastroenterology', 'Hepatology', 'Diagnostic Endoscopy'],
  'Pulmonology': ['Respiratory Medicine', 'Critical Care Pulmonology', 'Sleep Medicine'],
  'Psychiatry': ['General Psychiatry', 'Child & Adolescent Psychiatry', 'Addiction Medicine']
};

export default function HospitalAdminDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('doctors');
  const [doctors, setDoctors] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: 'Dr.',
    name: '',
    email: '',
    password: '',
    phone_number: '',
    department: 'General Medicine',
    specialization: 'Internal Medicine'
  });

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      // The backend will automatically infer hospital_id from the user's JWT token
      const res = await api.get('/doctors/list');
      setDoctors(res.data);
    } catch (error) {
      console.error("Failed to fetch doctors", error);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert("Please enter doctor's name");
      return;
    }
    setLoading(true);
    try {
      const payload = {
        title: formData.title,
        name: formData.name.trim(),
        username: `${formData.title} ${formData.name.trim()}`,
        email: formData.email.trim(),
        password: formData.password,
        phone_number: formData.phone_number.trim(),
        department: formData.department,
        specialization: formData.specialization
      };

      await api.post('/doctors/register', payload);
      alert("Doctor registered successfully!");
      setShowAddModal(false);
      setFormData({
        title: 'Dr.',
        name: '',
        email: '',
        password: '',
        phone_number: '',
        department: 'General Medicine',
        specialization: 'Internal Medicine'
      });
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
          <div className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => setActiveTab('analytics')}>
            <BarChart3 size={20} />
            Population Analytics
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
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: activeTab === 'analytics' ? '1.5rem 2rem' : '3rem 4rem' }}>
        {activeTab === 'doctors' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Doctor Faculty Directory
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Onboard physicians, assign medical departments, and manage credentials.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowAddModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Plus size={18} /> Register Doctor
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden', borderRadius: '14px', boxShadow: 'var(--shadow-sm)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-light)', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Doctor</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Department</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Specialization</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Contact Info</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Status</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.length === 0 ? (
                    <tr>
                      <td colSpan="6" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        <Stethoscope size={36} color="var(--accent-blue)" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
                        <div style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-primary)' }}>No Doctors Registered</div>
                        <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>Click "Register Doctor" above to onboard your first faculty member.</div>
                      </td>
                    </tr>
                  ) : (
                    doctors.map(doc => {
                      const docName = doc.name || doc.username || (doc.user?.username ? doc.user.username : `Doctor #${doc.id}`);
                      const dept = doc.department || doc.department_name || (typeof doc.department === 'string' ? doc.department : 'General Medicine');
                      const spec = doc.specialization || doc.qualification || dept;
                      const email = doc.email || doc.user?.email || 'N/A';
                      const phone = doc.phone_number || doc.user?.phone_number || '';
                      
                      return (
                        <tr key={doc.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                          <td style={{ padding: '1.25rem 1.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(2, 132, 199, 0.1)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                                {docName.replace(/^Dr\.\s*|^Prof\.\s*Dr\.\s*/i, '').slice(0, 2).toUpperCase()}
                              </div>
                              <div>
                                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>{docName}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Faculty ID: #{doc.id}</div>
                              </div>
                            </div>
                          </td>
                          <td style={{ padding: '1.25rem 1.5rem' }}>
                            <span style={{ background: 'rgba(2, 132, 199, 0.08)', color: 'var(--accent-blue)', padding: '0.25rem 0.65rem', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 600 }}>
                              {dept}
                            </span>
                          </td>
                          <td style={{ padding: '1.25rem 1.5rem', color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 500 }}>
                            {spec}
                          </td>
                          <td style={{ padding: '1.25rem 1.5rem' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 500 }}>{email}</div>
                            {phone && <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{phone}</div>}
                          </td>
                          <td style={{ padding: '1.25rem 1.5rem' }}>
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--accent-green)', padding: '0.2rem 0.65rem', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600 }}>
                              ● Active
                            </span>
                          </td>
                          <td style={{ padding: '1.25rem 1.5rem', textAlign: 'right' }}>
                            <button className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>Manage</button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'analytics' && (
          <PopulationDashboard />
        )}

        {activeTab === 'settings' && (
          <div className="glass-panel" style={{ background: 'white', padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)', borderRadius: '14px' }}>
            <h3>Hospital Facility Configuration</h3>
            <p style={{ marginTop: '0.5rem' }}>Configure departments, consultation rooms, and operational schedules.</p>
          </div>
        )}
      </div>

      {/* Add Doctor Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2.25rem', width: '100%', maxWidth: '580px', maxHeight: '90vh', overflowY: 'auto', borderRadius: '16px', boxShadow: 'var(--shadow-xl)', position: 'relative' }}>
            <button 
              onClick={() => setShowAddModal(false)}
              style={{ position: 'absolute', right: '1.25rem', top: '1.25rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
            >
              <X size={20} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(2, 132, 199, 0.1)', padding: '0.5rem', borderRadius: '10px' }}>
                <Stethoscope color="var(--accent-blue)" size={24} />
              </div>
              <div>
                <h2 style={{ fontSize: '1.35rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Register New Doctor</h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Add physician to hospital roster with clinical credentials</div>
              </div>
            </div>

            <form onSubmit={handleRegister}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                {/* Title + Name */}
                <div className="input-group" style={{ gridColumn: 'span 2' }}>
                  <label className="input-label" style={{ fontWeight: 600 }}>Doctor Full Name</label>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <select 
                      className="input-field" 
                      style={{ width: '130px', flexShrink: 0 }}
                      value={formData.title}
                      onChange={e => setFormData({ ...formData, title: e.target.value })}
                    >
                      <option value="Dr.">Dr.</option>
                      <option value="Prof. Dr.">Prof. Dr.</option>
                      <option value="Assoc. Prof. Dr.">Assoc. Prof. Dr.</option>
                      <option value="Mr.">Mr.</option>
                      <option value="Ms.">Ms.</option>
                    </select>
                    <input 
                      type="text" 
                      className="input-field" 
                      required 
                      placeholder="e.g. Vikram Malhotra" 
                      value={formData.name}
                      onChange={e => setFormData({ ...formData, name: e.target.value })} 
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="input-group">
                  <label className="input-label" style={{ fontWeight: 600 }}>Email Address</label>
                  <input 
                    type="email" 
                    className="input-field" 
                    required 
                    placeholder="doctor@hospital.org"
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })} 
                  />
                </div>

                {/* Password */}
                <div className="input-group">
                  <label className="input-label" style={{ fontWeight: 600 }}>Password</label>
                  <input 
                    type="password" 
                    className="input-field" 
                    required 
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={e => setFormData({ ...formData, password: e.target.value })} 
                  />
                </div>

                {/* Phone */}
                <div className="input-group" style={{ gridColumn: 'span 2' }}>
                  <label className="input-label" style={{ fontWeight: 600 }}>Phone Number</label>
                  <input 
                    type="tel" 
                    className="input-field" 
                    required 
                    placeholder="e.g. 9876543210"
                    value={formData.phone_number}
                    onChange={e => setFormData({ ...formData, phone_number: e.target.value })} 
                  />
                </div>

                {/* Department Dropdown */}
                <div className="input-group">
                  <label className="input-label" style={{ fontWeight: 600 }}>Department</label>
                  <select 
                    className="input-field"
                    value={formData.department}
                    onChange={e => {
                      const dept = e.target.value;
                      const specs = DEPARTMENT_SPECIALIZATIONS[dept] || [];
                      setFormData({
                        ...formData,
                        department: dept,
                        specialization: specs[0] || 'General'
                      });
                    }}
                  >
                    {Object.keys(DEPARTMENT_SPECIALIZATIONS).map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>

                {/* Specialization Dropdown */}
                <div className="input-group">
                  <label className="input-label" style={{ fontWeight: 600 }}>Specialization</label>
                  <select 
                    className="input-field"
                    value={formData.specialization}
                    onChange={e => setFormData({ ...formData, specialization: e.target.value })}
                  >
                    {(DEPARTMENT_SPECIALIZATIONS[formData.department] || []).map(spec => (
                      <option key={spec} value={spec}>{spec}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.75rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1.5, background: 'var(--accent-blue)' }} disabled={loading}>
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
