import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Search, Users, FlaskConical, AlertTriangle, Settings, 
  Stethoscope, ScanLine, MoreHorizontal, ChevronRight,
  PlusCircle, FileText, Pill, ShieldAlert, Bot, X, CheckCircle, Clock
} from 'lucide-react';
import api from '../api';
import MedicalTimeline from './timeline/MedicalTimeline';
import RAGChatInterface from './copilot/RAGChatInterface';
import PrescriptionAssistant from './copilot/PrescriptionAssistant';
import BiomarkerTrendChart from './analytics/BiomarkerTrendChart';

export default function DoctorDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('search');
  const [selectedBiomarker, setSelectedBiomarker] = useState('HbA1c');
  
  // Data States
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientSummary, setPatientSummary] = useState(null);
  const [patients, setPatients] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);
  
  // Copilot Drawer
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  
  // Clinical Modals
  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false);
  const [diagnosisData, setDiagnosisData] = useState({ condition_name: '', severity: 'Moderate', clinical_notes: '', icd10_code: '' });
  
  const [showPrescriptionModal, setShowPrescriptionModal] = useState(false);
  const [medications, setMedications] = useState([{ name: '', dosage: '', frequency: '' }]);
  const [prescriptionInstructions, setPrescriptionInstructions] = useState('');
  
  const [showLabOrderModal, setShowLabOrderModal] = useState(false);
  const [labOrderData, setLabOrderData] = useState({ tests: 'CBC, Lipid Profile', clinical_notes: '' });
  
  const [submittingAction, setSubmittingAction] = useState(false);

  useEffect(() => {
    fetchAlerts();
    fetchPatients();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/alerts/');
      setAlerts(res.data || []);
    } catch (err) {
      console.error("Failed to fetch alerts:", err);
    }
  };

  const fetchPatients = async () => {
    setLoadingPatients(true);
    try {
      const res = await api.get('/patients/list');
      setPatients(res.data || []);
    } catch (err) {
      console.error("Failed to fetch patients list:", err);
    } finally {
      setLoadingPatients(false);
    }
  };

  const handleSearchPatient = async (targetId) => {
    const idToSearch = targetId || searchQuery.trim();
    if (!idToSearch) return;
    
    setSearchLoading(true);
    try {
      const res = await api.get(`/patients/profile?health_id=${idToSearch}`);
      setSelectedPatient(res.data);
      setActiveTab('search');
      
      // Also fetch patient structured health summary
      try {
        const sumRes = await api.get(`/patients/${idToSearch}/health-summary`);
        setPatientSummary(sumRes.data);
      } catch (sumErr) {
        setPatientSummary(null);
      }
    } catch (err) {
      alert("Patient not found: " + (err.response?.data?.detail || err.message));
    } finally {
      setSearchLoading(false);
    }
  };

  const handleMarkAlertRead = async (alertId) => {
    try {
      await api.put(`/alerts/${alertId}/read`);
      setAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (err) {
      alert("Failed to mark alert as read: " + err.message);
    }
  };

  // Clinical Actions
  const handleRecordDiagnosis = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;
    setSubmittingAction(true);
    try {
      await api.post('/records/create', {
        record_type: 'diagnosis',
        data: diagnosisData,
        health_id: selectedPatient.health_id
      });
      alert("Diagnosis recorded successfully!");
      setShowDiagnosisModal(false);
      setDiagnosisData({ condition_name: '', severity: 'Moderate', clinical_notes: '', icd10_code: '' });
      handleSearchPatient(selectedPatient.health_id);
    } catch (err) {
      alert("Failed to record diagnosis: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleAddMedicationRow = () => {
    setMedications([...medications, { name: '', dosage: '', frequency: '' }]);
  };

  const handleMedChange = (index, field, value) => {
    const updated = [...medications];
    updated[index][field] = value;
    setMedications(updated);
  };

  const handleIssuePrescription = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;
    const validMeds = medications.filter(m => m.name.trim());
    if (validMeds.length === 0) {
      alert("Please enter at least one medication.");
      return;
    }

    setSubmittingAction(true);
    try {
      await api.post('/records/create', {
        record_type: 'prescription',
        data: {
          medications: validMeds,
          instructions: prescriptionInstructions
        },
        health_id: selectedPatient.health_id
      });
      alert("E-Prescription issued and cryptographically signed!");
      setShowPrescriptionModal(false);
      setMedications([{ name: '', dosage: '', frequency: '' }]);
      setPrescriptionInstructions('');
      handleSearchPatient(selectedPatient.health_id);
    } catch (err) {
      alert("Failed to issue prescription: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleOrderLab = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;
    setSubmittingAction(true);
    try {
      const testsArray = labOrderData.tests.split(',').map(t => ({ name: t.trim(), priority: 'Routine' }));
      await api.post('/records/create', {
        record_type: 'lab_order',
        data: {
          tests: testsArray,
          clinical_notes: labOrderData.clinical_notes
        },
        health_id: selectedPatient.health_id
      });
      alert("Lab order dispatched to hospital laboratory!");
      setShowLabOrderModal(false);
      setLabOrderData({ tests: 'CBC, Lipid Profile', clinical_notes: '' });
      handleSearchPatient(selectedPatient.health_id);
    } catch (err) {
      alert("Failed to order lab: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)', display: 'flex' }}>
      
      {/* Sidebar */}
      <div className="sidebar-light" style={{ width: '260px', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Stethoscope color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>HealthID AI</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>Dr. {user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div 
            className={`nav-item ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search size={20} />
            Search Patient
          </div>
          <div 
            className={`nav-item ${activeTab === 'patients' ? 'active' : ''}`}
            onClick={() => setActiveTab('patients')}
          >
            <Users size={20} />
            My Patients ({patients.length})
          </div>
          <div 
            className={`nav-item ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <AlertTriangle size={20} />
            Alerts {alerts.length > 0 && <span style={{ marginLeft: 'auto', background: 'var(--accent-red)', color: 'white', padding: '0.15rem 0.5rem', borderRadius: '10px', fontSize: '0.75rem' }}>{alerts.length}</span>}
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ flex: 1, padding: '2.5rem 3.5rem', overflowY: 'auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
              Doctor Clinical Station
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem' }}>
              Instant ABHA/HealthID lookup, AI copilot intelligence, and paperless prescription management.
            </p>
          </div>
          {selectedPatient && (
            <button 
              className="btn btn-primary" 
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#4f46e5' }}
              onClick={() => setIsCopilotOpen(true)}
            >
              <Bot size={18} /> Ask AI Copilot
            </button>
          )}
        </div>

        {/* Global Stats Overview */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500, marginBottom: '0.5rem' }}>Enrolled Patients</div>
            <div style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000' }}>{patients.length}</div>
          </div>
          <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500, marginBottom: '0.5rem' }}>Active Clinical Alerts</div>
            <div style={{ fontSize: '2.25rem', fontWeight: 600, color: alerts.length > 0 ? 'var(--accent-red)' : '#000' }}>{alerts.length}</div>
          </div>
          <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500, marginBottom: '0.5rem' }}>Active Patient Scoped</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 600, color: selectedPatient ? 'var(--accent-blue)' : 'var(--text-tertiary)' }}>
              {selectedPatient ? selectedPatient.full_name || selectedPatient.health_id : 'None selected'}
            </div>
          </div>
        </div>

        {/* TAB 1: SEARCH & PATIENT DOSSIER */}
        {activeTab === 'search' && (
          <div>
            {/* Search Input Bar */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ position: 'relative', width: '350px' }}>
                <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input 
                  type="text" 
                  className="input-field" 
                  style={{ paddingLeft: '2.75rem', height: '100%', margin: 0 }}
                  placeholder="Enter Patient Health ID (e.g. 21-4921-2918-0912)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleSearchPatient(); }}
                />
              </div>
              <button 
                className="btn btn-primary" 
                style={{ padding: '0.75rem 1.5rem', fontWeight: 500 }}
                onClick={() => handleSearchPatient()}
                disabled={searchLoading}
              >
                {searchLoading ? 'Searching...' : 'Pull Records'}
              </button>
            </div>

            {/* Selected Patient Dossier View */}
            {selectedPatient ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                
                {/* Patient Header Card */}
                <div className="glass-panel" style={{ padding: '1.75rem', background: 'white', borderRadius: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <h2 style={{ fontSize: '1.75rem', margin: 0, color: '#000' }}>
                          {selectedPatient.full_name || 'Patient'}
                        </h2>
                        <span style={{ background: '#e0e7ff', color: '#3730a3', padding: '0.2rem 0.6rem', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 600 }}>
                          {selectedPatient.health_id}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                        <span><strong>Blood Group:</strong> {selectedPatient.blood_group || 'Unknown'}</span>
                        <span><strong>Gender:</strong> {selectedPatient.gender || 'Not specified'}</span>
                        <span><strong>DOB:</strong> {selectedPatient.dob || 'Unknown'}</span>
                        <span><strong>Emergency:</strong> {selectedPatient.emergency_contact_phone || 'None'}</span>
                      </div>
                    </div>

                    {/* Action Bar */}
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                      <button className="btn btn-secondary" onClick={() => setShowDiagnosisModal(true)}>
                        <FileText size={16} /> Add Diagnosis
                      </button>
                      <button className="btn btn-primary" style={{ background: '#10b981' }} onClick={() => setShowPrescriptionModal(true)}>
                        <Pill size={16} /> E-Prescribe
                      </button>
                      <button className="btn btn-secondary" onClick={() => setShowLabOrderModal(true)}>
                        <FlaskConical size={16} /> Order Lab
                      </button>
                    </div>
                  </div>

                  {/* Badges for Allergies & Chronic Conditions */}
                  <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', gap: '2rem' }}>
                    <div>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)', fontWeight: 600, textTransform: 'uppercase' }}>Known Allergies</span>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.35rem', flexWrap: 'wrap' }}>
                        {selectedPatient.known_allergies && selectedPatient.known_allergies.length > 0 ? (
                          selectedPatient.known_allergies.map((a, i) => (
                            <span key={i} style={{ background: '#fee2e2', color: '#b91c1c', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 500 }}>
                              ⚠️ {a}
                            </span>
                          ))
                        ) : (
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>No known allergies</span>
                        )}
                      </div>
                    </div>

                    <div>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)', fontWeight: 600, textTransform: 'uppercase' }}>Chronic Conditions</span>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.35rem', flexWrap: 'wrap' }}>
                        {selectedPatient.chronic_diseases && selectedPatient.chronic_diseases.length > 0 ? (
                          selectedPatient.chronic_diseases.map((d, i) => (
                            <span key={i} style={{ background: '#e0f2fe', color: '#0369a1', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 500 }}>
                              {d}
                            </span>
                          ))
                        ) : (
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>None recorded</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Medical Timeline Feed */}
                <div className="glass-panel" style={{ padding: '1.75rem', background: 'white', borderRadius: '16px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', color: '#000' }}>
                    Longitudinal Medical Timeline
                  </h3>
                  <MedicalTimeline healthId={selectedPatient.health_id} />
                </div>

                {/* Longitudinal Biomarker Monitoring */}
                <div className="glass-panel" style={{ padding: '1.75rem', background: 'white', borderRadius: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: '#000' }}>
                        Biomarker Trend Tracker
                      </h3>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        Longitudinal clinical biomarker progression over time
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      {['HbA1c', 'Glucose', 'Cholesterol', 'Creatinine'].map(bm => (
                        <button
                          key={bm}
                          type="button"
                          className={`btn ${selectedBiomarker === bm ? 'btn-primary' : 'btn-secondary'}`}
                          style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', borderRadius: '6px' }}
                          onClick={() => setSelectedBiomarker(bm)}
                        >
                          {bm}
                        </button>
                      ))}
                    </div>
                  </div>
                  <BiomarkerTrendChart healthId={selectedPatient.health_id} biomarker={selectedBiomarker} />
                </div>

              </div>
            ) : (
              /* If no patient is selected, display recent list */
              <div>
                <h3 style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', fontWeight: 500, marginBottom: '1rem' }}>
                  Enrolled Clinic Patients
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {patients.map(p => (
                    <div 
                      key={p.id} 
                      className="glass-panel hover-card" 
                      style={{ display: 'flex', alignItems: 'center', padding: '1.25rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', cursor: 'pointer' }}
                      onClick={() => handleSearchPatient(p.health_id)}
                    >
                      <div style={{ width: '44px', height: '44px', borderRadius: '22px', background: 'var(--accent-blue-light)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, marginRight: '1rem' }}>
                        {p.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, color: '#000', fontSize: '1.05rem' }}>{p.name}</div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{p.health_id} | Blood Group: {p.blood_group || 'N/A'}</div>
                      </div>
                      <ChevronRight color="var(--text-tertiary)" size={20} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: MY PATIENTS */}
        {activeTab === 'patients' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>Patient Directory</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {patients.map(p => (
                <div 
                  key={p.id} 
                  className="glass-panel hover-card" 
                  style={{ display: 'flex', alignItems: 'center', padding: '1.25rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', cursor: 'pointer' }}
                  onClick={() => handleSearchPatient(p.health_id)}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: '#000' }}>{p.name}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Health ID: {p.health_id}</div>
                  </div>
                  <button className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>Open Dossier</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: ALERTS */}
        {activeTab === 'alerts' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>Active Clinical Alerts</h2>
            {alerts.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)' }}>No active unread alerts for your patients.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {alerts.map(a => (
                  <div key={a.id} className="glass-panel" style={{ padding: '1.25rem', background: 'white', borderLeft: '4px solid var(--accent-red)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span style={{ fontWeight: 600, color: 'var(--accent-red)' }}>{a.alert_type}</span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>{a.created_at ? new Date(a.created_at).toLocaleDateString() : ''}</span>
                      </div>
                      <div style={{ color: '#000', fontSize: '0.95rem' }}>{a.message}</div>
                    </div>
                    <button className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem' }} onClick={() => handleMarkAlertRead(a.id)}>
                      Mark Read
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>

      {/* SLIDING COPILOT DRAWER */}
      {isCopilotOpen && selectedPatient && (
        <div style={{
          position: 'fixed', right: 0, top: 0, bottom: 0, width: '420px',
          background: 'white', boxShadow: '-4px 0 20px rgba(0,0,0,0.1)', zIndex: 1000,
          display: 'flex', flexDirection: 'column'
        }}>
          <div style={{ padding: '1.25rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Bot color="#4f46e5" size={22} />
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Clinical Copilot RAG</h3>
            </div>
            <button onClick={() => setIsCopilotOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
              <X size={20} color="var(--text-tertiary)" />
            </button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
            <RAGChatInterface healthId={selectedPatient.health_id} />
          </div>
        </div>
      )}

      {/* MODAL 1: RECORD DIAGNOSIS */}
      {showDiagnosisModal && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h3 style={{ margin: 0 }}>Record Clinical Diagnosis</h3>
              <button onClick={() => setShowDiagnosisModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            <form onSubmit={handleRecordDiagnosis}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Condition Name</label>
                <input 
                  type="text" 
                  className="input-field" 
                  required
                  placeholder="e.g. Type 2 Diabetes Mellitus"
                  value={diagnosisData.condition_name}
                  onChange={(e) => setDiagnosisData({ ...diagnosisData, condition_name: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Severity</label>
                <select 
                  className="input-field"
                  value={diagnosisData.severity}
                  onChange={(e) => setDiagnosisData({ ...diagnosisData, severity: e.target.value })}
                >
                  <option value="Mild">Mild</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Severe">Severe</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Clinical Notes</label>
                <textarea 
                  className="input-field" 
                  rows={3}
                  placeholder="Clinical observation, symptoms, and plan..."
                  value={diagnosisData.clinical_notes}
                  onChange={(e) => setDiagnosisData({ ...diagnosisData, clinical_notes: e.target.value })}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submittingAction}>
                {submittingAction ? 'Saving...' : 'Save Diagnosis'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: E-PRESCRIPTION WITH LIVE COPILOT SAFETY */}
      {showPrescriptionModal && selectedPatient && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '620px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h3 style={{ margin: 0 }}>Issue E-Prescription</h3>
              <button onClick={() => setShowPrescriptionModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            
            {/* Live Copilot Safety Checks */}
            <div style={{ marginBottom: '1.25rem' }}>
              <PrescriptionAssistant 
                healthId={selectedPatient.health_id} 
                proposedMedications={medications.filter(m => m.name.trim())} 
              />
            </div>

            <form onSubmit={handleIssuePrescription}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>Prescribed Medications</label>
                {medications.map((med, idx) => (
                  <div key={idx} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ margin: 0 }}
                      placeholder="Medicine Name (e.g. Metformin)" 
                      value={med.name} 
                      onChange={(e) => handleMedChange(idx, 'name', e.target.value)} 
                    />
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ margin: 0 }}
                      placeholder="Dosage (500mg)" 
                      value={med.dosage} 
                      onChange={(e) => handleMedChange(idx, 'dosage', e.target.value)} 
                    />
                    <input 
                      type="text" 
                      className="input-field" 
                      style={{ margin: 0 }}
                      placeholder="Freq (1/day)" 
                      value={med.frequency} 
                      onChange={(e) => handleMedChange(idx, 'frequency', e.target.value)} 
                    />
                  </div>
                ))}
                <button type="button" className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.85rem', marginTop: '0.25rem' }} onClick={handleAddMedicationRow}>
                  + Add Another Medicine
                </button>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Instructions / Dietary Advice</label>
                <textarea 
                  className="input-field" 
                  rows={2}
                  placeholder="Take after meals. Drink plenty of fluids..."
                  value={prescriptionInstructions}
                  onChange={(e) => setPrescriptionInstructions(e.target.value)}
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', background: '#10b981' }} disabled={submittingAction}>
                {submittingAction ? 'Signing & Issuing...' : 'Sign & Issue E-Prescription'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: ORDER LAB TEST */}
      {showLabOrderModal && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h3 style={{ margin: 0 }}>Order Laboratory Diagnostics</h3>
              <button onClick={() => setShowLabOrderModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={20} /></button>
            </div>
            <form onSubmit={handleOrderLab}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Required Tests (Comma-separated)</label>
                <input 
                  type="text" 
                  className="input-field" 
                  required
                  placeholder="e.g. CBC, HbA1c, Serum Creatinine"
                  value={labOrderData.tests}
                  onChange={(e) => setLabOrderData({ ...labOrderData, tests: e.target.value })}
                />
              </div>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Clinical Indications & Notes</label>
                <textarea 
                  className="input-field" 
                  rows={3}
                  placeholder="Suspected diabetic nephropathy. Fasting specimen required..."
                  value={labOrderData.clinical_notes}
                  onChange={(e) => setLabOrderData({ ...labOrderData, clinical_notes: e.target.value })}
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submittingAction}>
                {submittingAction ? 'Dispatching...' : 'Dispatch Lab Order'}
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
