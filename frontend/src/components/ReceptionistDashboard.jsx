import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Calendar, UserPlus, Search, Clock, QrCode, CreditCard, PlusCircle } from 'lucide-react';
import api from '../api';

export default function ReceptionistDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('register');
  const [showModal, setShowModal] = useState(false);
  const [showBillingModal, setShowBillingModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  
  // Registration Success State
  const [newPatient, setNewPatient] = useState(null);

  const [formData, setFormData] = useState({
    username: '', password: '', email: '', phone_number: '',
    blood_group: '', emergency_contact_name: '', emergency_contact_phone: ''
  });

  const [invoiceData, setInvoiceData] = useState({
    health_id: '', description: 'General Medical Consultation', amount: '50.00'
  });

  React.useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const res = await api.get('/patients/list');
      setPatients(res.data);
    } catch (error) {
      console.error("Failed to fetch patients", error);
    }
  };

  const fetchAppointments = async () => {
    try {
      const res = await api.get('/appointments/list');
      setAppointments(res.data);
    } catch (error) {
      console.error("Failed to fetch appointments", error);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'appointments') {
      fetchAppointments();
    }
  }, [activeTab]);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/patients/register', formData);
      setNewPatient(res.data);
      setShowModal(false);
      setFormData({
        username: '', password: '', email: '', phone_number: '',
        blood_group: '', emergency_contact_name: '', emergency_contact_phone: ''
      });
      fetchPatients();
    } catch (error) {
      alert("Registration failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const amountInCents = Math.round(parseFloat(invoiceData.amount) * 100);
      const payload = {
        health_id: invoiceData.health_id,
        description: invoiceData.description,
        currency: 'USD',
        line_items: [{ description: invoiceData.description, amount: amountInCents }]
      };
      await api.post('/billing/invoices/create', payload);
      alert("Invoice generated successfully!");
      setShowBillingModal(false);
      setInvoiceData({ health_id: '', description: 'General Medical Consultation', amount: '50.00' });
    } catch (error) {
      alert("Failed to generate invoice: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Calendar color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Front Desk</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div className={`nav-item ${activeTab === 'register' ? 'active' : ''}`} onClick={() => setActiveTab('register')}>
            <UserPlus size={20} />
            Patient Onboarding
          </div>
          <div className={`nav-item ${activeTab === 'search' ? 'active' : ''}`} onClick={() => setActiveTab('search')}>
            <Search size={20} />
            Search Records
          </div>
          <div className={`nav-item ${activeTab === 'appointments' ? 'active' : ''}`} onClick={() => setActiveTab('appointments')}>
            <Clock size={20} />
            Appointments
          </div>
          <div className={`nav-item ${activeTab === 'billing' ? 'active' : ''}`} onClick={() => setActiveTab('billing')}>
            <CreditCard size={20} />
            Billing & Invoices
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        
        {activeTab === 'register' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Patient Onboarding
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Register a new patient and generate their Health ID and QR code.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => { setShowModal(true); setNewPatient(null); }}>
                <UserPlus size={18} /> New Patient
              </button>
            </div>

            {newPatient ? (
              <div className="glass-panel" style={{ background: 'white', padding: '3rem', textAlign: 'center', maxWidth: '600px', margin: '0 auto', borderRadius: '16px' }}>
                <div style={{ display: 'inline-flex', padding: '1rem', background: 'var(--accent-blue-light)', borderRadius: '50%', marginBottom: '1.5rem' }}>
                  <QrCode size={48} color="var(--accent-blue)" />
                </div>
                <h2 style={{ color: '#000', fontSize: '2rem', marginBottom: '0.5rem' }}>Registration Successful</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '2rem' }}>
                  The 14-digit Health ID has been securely generated.
                </p>
                
                <div style={{ background: 'var(--bg-tertiary)', padding: '2rem', borderRadius: '12px', marginBottom: '2rem' }}>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                    Official Health ID
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#000', letterSpacing: '0.1em' }}>
                    {newPatient.health_id}
                  </div>
                </div>

                <div style={{ border: '1px solid var(--border-light)', padding: '1.5rem', borderRadius: '12px', display: 'inline-block' }}>
                  <img src={`http://localhost:8000/${newPatient.qr_code_path}`} alt="Patient QR Code" style={{ width: '200px', height: '200px' }} />
                  <div style={{ marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Scan to view AI medical summary</div>
                </div>
                
                <div style={{ marginTop: '2rem' }}>
                  <button className="btn btn-secondary" onClick={() => setNewPatient(null)}>Done</button>
                </div>
              </div>
            ) : (
              <div className="glass-panel" style={{ background: 'white', padding: '4rem', textAlign: 'center', color: 'var(--text-tertiary)' }}>
                Click "New Patient" to begin the registration process.
              </div>
            )}
          </>
        )}

        {activeTab === 'search' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Patient Records
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Search and manage all registered patients.
                </p>
              </div>
              <div style={{ position: 'relative', width: '300px' }}>
                <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input 
                  type="text" 
                  className="input-field" 
                  style={{ paddingLeft: '2.75rem', margin: 0 }}
                  placeholder="Search by ID or Name..."
                />
              </div>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Health ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Patient Name</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Phone</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Blood Group</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map(patient => (
                    <tr key={patient.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--accent-blue)', fontWeight: 500 }}>{patient.health_id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{patient.name}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{patient.phone}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{patient.blood_group}</td>
                      <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                        <button className="btn btn-secondary" style={{ padding: '0.4rem' }}>View Profile</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'appointments' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Appointments
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Manage scheduled appointments for all doctors.
                </p>
              </div>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Patient ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Doctor ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Start Time</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.length === 0 && (
                    <tr><td colSpan="5" style={{ padding: '1rem 1.5rem', textAlign: 'center' }}>No appointments found.</td></tr>
                  )}
                  {appointments.map(apt => (
                    <tr key={apt.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--accent-blue)', fontWeight: 500 }}>{apt.id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{apt.patient_id}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{apt.doctor_id}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{new Date(apt.start_time).toLocaleString()}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{apt.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'billing' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Billing & Invoicing
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Issue consultation bills and manage patient invoices.
                </p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowBillingModal(true)}>
                <PlusCircle size={18} /> Issue New Bill
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '3rem', textAlign: 'center', borderRadius: '16px' }}>
              <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                Click "Issue New Bill" to generate an invoice for a patient by entering their 14-digit Health ID.
              </p>
            </div>
          </>
        )}
      </div>

      {/* Registration Modal */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2.5rem', width: '550px', maxHeight: '90vh', overflowY: 'auto', borderRadius: '16px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#000' }}>Register Patient</h2>
            <form onSubmit={handleRegister}>
              <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Account Details</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div className="input-group">
                  <label className="input-label">Username / Full Name</label>
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
                  <label className="input-label">Phone Number</label>
                  <input className="input-field" required onChange={e => setFormData({...formData, phone_number: e.target.value})} />
                </div>
              </div>

              <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Emergency & Medical Basics</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="input-group">
                  <label className="input-label">Blood Group</label>
                  <input className="input-field" placeholder="e.g. O+" onChange={e => setFormData({...formData, blood_group: e.target.value})} />
                </div>
                <div className="input-group">
                  <label className="input-label">Emergency Contact Name</label>
                  <input className="input-field" onChange={e => setFormData({...formData, emergency_contact_name: e.target.value})} />
                </div>
                <div className="input-group" style={{ gridColumn: 'span 2' }}>
                  <label className="input-label">Emergency Contact Phone</label>
                  <input className="input-field" onChange={e => setFormData({...formData, emergency_contact_phone: e.target.value})} />
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1, background: 'var(--accent-blue)' }} disabled={loading}>
                  {loading ? 'Generating ID...' : 'Register & Generate ID'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Billing Invoice Modal */}
      {showBillingModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2.5rem', width: '500px', borderRadius: '16px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#000' }}>Generate Patient Invoice</h2>
            <form onSubmit={handleCreateInvoice}>
              <div className="input-group">
                <label className="input-label">Patient Health ID (14-Digit)</label>
                <input
                  className="input-field"
                  placeholder="e.g. 91-4820-1934-8851"
                  value={invoiceData.health_id}
                  onChange={e => setInvoiceData({...invoiceData, health_id: e.target.value})}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label">Description / Service</label>
                <input
                  className="input-field"
                  value={invoiceData.description}
                  onChange={e => setInvoiceData({...invoiceData, description: e.target.value})}
                  required
                />
              </div>
              <div className="input-group">
                <label className="input-label">Amount ($ USD)</label>
                <input
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={invoiceData.amount}
                  onChange={e => setInvoiceData({...invoiceData, amount: e.target.value})}
                  required
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowBillingModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1, background: 'var(--accent-blue)' }} disabled={loading}>
                  {loading ? 'Issuing Bill...' : 'Generate Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

