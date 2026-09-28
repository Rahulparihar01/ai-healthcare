import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Microscope, CheckCircle2, FileText, Search, UploadCloud, FileCheck, AlertCircle, Clock, X } from 'lucide-react';
import api from '../api';

export default function LabTechnicianDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('pending');
  const [orders, setOrders] = useState([]);
  const [historyOrders, setHistoryOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');
  
  // Results upload state
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [resultsData, setResultsData] = useState('');
  const [technicianNotes, setTechnicianNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  useEffect(() => {
    fetchOrders();
    fetchHistory();
  }, []);

  const fetchOrders = async () => {
    try {
      const res = await api.get('/labs/pending');
      setOrders(res.data);
    } catch (error) {
      console.error("Failed to fetch pending lab orders", error);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await api.get('/labs/history');
      setHistoryOrders(res.data);
    } catch (error) {
      console.error("Failed to fetch lab orders history", error);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.match(/\.(pdf|jpg|jpeg|png)$/i)) {
        alert("Please upload a valid PDF or image file (PDF, PNG, JPG).");
        return;
      }
      setUploadFile(file);
    }
  };

  const handleCompleteOrder = async (e) => {
    e.preventDefault();
    if (!uploadFile && !resultsData.trim()) {
      alert("Please either upload a lab report document (PDF/Image) or enter structured findings.");
      return;
    }

    setSubmitting(true);
    setStatusMessage({ type: 'info', text: 'Processing report and initiating AI OCR ingestion...' });

    try {
      let fileUrl = null;

      // 1. If a file is attached, upload via /records/upload to trigger Celery OCR
      if (uploadFile) {
        const formData = new FormData();
        formData.append('file', uploadFile);
        formData.append('record_type', 'lab_report');
        formData.append('health_id', selectedOrder.patient_health_id || `PAT-${selectedOrder.patient_id}`);
        if (selectedOrder.visit_id) {
          formData.append('visit_id', selectedOrder.visit_id);
        }

        const uploadRes = await api.post('/records/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        fileUrl = uploadRes.data.file_url;
      }

      // 2. Parse structured findings if entered
      let resultsJson = {};
      if (resultsData.trim()) {
        try {
          resultsJson = JSON.parse(resultsData);
        } catch {
          resultsJson = { summary: resultsData };
        }
      } else if (uploadFile) {
        resultsJson = {
          file_name: uploadFile.name,
          status: "Queued for automated AI OCR biomarker extraction"
        };
      }

      // 3. Mark the lab order as Completed
      await api.post(`/labs/orders/${selectedOrder.id}/complete`, {
        results: resultsJson,
        notes: technicianNotes,
        file_url: fileUrl
      });

      setStatusMessage({ type: 'success', text: 'Lab order completed successfully and findings attached to patient timeline.' });
      setTimeout(() => {
        setSelectedOrder(null);
        setUploadFile(null);
        setResultsData('');
        setTechnicianNotes('');
        setStatusMessage(null);
        fetchOrders();
        fetchHistory();
      }, 1200);

    } catch (error) {
      console.error("Failed to complete order:", error);
      setStatusMessage({
        type: 'error',
        text: "Failed to complete order: " + (error.response?.data?.detail || error.message)
      });
    } finally {
      setSubmitting(false);
    }
  };

  const filteredHistory = historyOrders.filter(o => {
    const q = searchFilter.toLowerCase();
    const idMatch = String(o.id).includes(q);
    const patMatch = (o.patient_name || '').toLowerCase().includes(q) || (o.patient_health_id || '').toLowerCase().includes(q);
    const testMatch = (o.tests || []).some(t => (t.name || '').toLowerCase().includes(q));
    return idMatch || patMatch || testMatch;
  });

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh', display: 'flex' }}>
      {/* Sidebar */}
      <div className="sidebar-light" style={{ width: '280px', flexShrink: 0, borderRight: '1px solid var(--border-light)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1.5rem 1.25rem', borderBottom: '1px solid var(--border-light)' }}>
          <div style={{ background: 'rgba(2, 132, 199, 0.1)', padding: '0.5rem', borderRadius: '10px' }}>
            <Microscope color="var(--accent-blue)" size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.15rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Lab Workstation</h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Diagnostic Station</span>
          </div>
        </div>
        
        <div style={{ padding: '1.25rem', borderBottom: '1px solid var(--border-light)', background: 'var(--bg-secondary)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Logged in as</div>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1rem' }}>{user?.username}</strong>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', marginTop: '0.2rem' }}>Role: Lab Technician</div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', padding: '1rem' }}>
          <div 
            className={`nav-item ${activeTab === 'pending' ? 'active' : ''}`} 
            onClick={() => setActiveTab('pending')}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', borderRadius: '8px', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <FileText size={18} />
              <span>Pending Orders</span>
            </div>
            {orders.length > 0 && (
              <span style={{ background: 'var(--accent-blue)', color: 'white', borderRadius: '12px', padding: '0.15rem 0.6rem', fontSize: '0.75rem', fontWeight: 600 }}>
                {orders.length}
              </span>
            )}
          </div>

          <div 
            className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} 
            onClick={() => setActiveTab('history')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem', borderRadius: '8px', cursor: 'pointer' }}
          >
            <Search size={18} />
            <span>Fulfillment History</span>
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '1.25rem', borderTop: '1px solid var(--border-light)' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Sign Out</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ flex: 1, backgroundColor: 'var(--bg-primary)', padding: '2.5rem 3.5rem', overflowY: 'auto' }}>
        
        {activeTab === 'pending' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                  Pending Diagnostic Orders
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                  Fulfill doctor test requests with automatic AI OCR analysis and patient timeline ingestion.
                </p>
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={fetchOrders}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Clock size={16} /> Refresh Queue
              </button>
            </div>

            <div className="glass-panel" style={{ background: 'white', borderRadius: '12px', boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-light)', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Order #</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Patient</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Requested Tests</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Notes / Priority</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600, textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        <CheckCircle2 size={36} color="var(--accent-green)" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
                        <div style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-primary)' }}>All Orders Completed</div>
                        <div style={{ fontSize: '0.9rem' }}>No pending laboratory test requests at this time.</div>
                      </td>
                    </tr>
                  ) : (
                    orders.map(order => (
                      <tr key={order.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td style={{ padding: '1.25rem 1.5rem', fontWeight: 700, color: 'var(--accent-blue)' }}>
                          #{order.id}
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{order.patient_name || `Patient #${order.patient_id}`}</div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{order.patient_health_id || 'ID Pending'}</div>
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem' }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                            {(order.tests || []).map((t, idx) => (
                              <span key={idx} style={{ background: 'rgba(2, 132, 199, 0.08)', color: 'var(--accent-blue)', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 500 }}>
                                {t.name || 'Test'}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '240px' }}>
                          {order.clinical_notes || <span style={{ color: 'var(--text-tertiary)', fontStyle: 'italic' }}>Standard routine</span>}
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem', textAlign: 'right' }}>
                          <button 
                            className="btn btn-primary" 
                            style={{ padding: '0.5rem 1.1rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }} 
                            onClick={() => {
                              setSelectedOrder(order);
                              setUploadFile(null);
                              setResultsData('');
                              setTechnicianNotes('');
                              setStatusMessage(null);
                            }}
                          >
                            <UploadCloud size={16} /> Process & Upload
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'history' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                  Fulfillment History
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
                  Track previously processed diagnostic orders and verify lab result deliveries.
                </p>
              </div>

              <div style={{ width: '320px', position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-secondary)' }} />
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="Filter by Order #, Patient, or Test..." 
                  value={searchFilter}
                  onChange={e => setSearchFilter(e.target.value)}
                  style={{ paddingLeft: '2.4rem' }}
                />
              </div>
            </div>

            <div className="glass-panel" style={{ background: 'white', borderRadius: '12px', boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-light)', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Order #</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Patient</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Tests Completed</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Date Processed</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No processed lab records found matching your filter.
                      </td>
                    </tr>
                  ) : (
                    filteredHistory.map(order => (
                      <tr key={order.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td style={{ padding: '1.25rem 1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                          #{order.id}
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{order.patient_name || `Patient #${order.patient_id}`}</div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{order.patient_health_id || 'N/A'}</div>
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem' }}>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                            {(order.tests || []).map((t, idx) => (
                              <span key={idx} style={{ background: 'rgba(34, 197, 94, 0.08)', color: 'var(--accent-green)', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 500 }}>
                                {t.name || 'Test'}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                          {order.created_at ? new Date(order.created_at).toLocaleDateString() + ' ' + new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                        </td>
                        <td style={{ padding: '1.25rem 1.5rem' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--accent-green)', padding: '0.25rem 0.65rem', borderRadius: '999px', fontSize: '0.8rem', fontWeight: 600 }}>
                            <CheckCircle2 size={13} /> Completed
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Upload Results & Fulfill Order Modal */}
      {selectedOrder && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2rem', width: '100%', maxWidth: '600px', borderRadius: '16px', boxShadow: 'var(--shadow-xl)', position: 'relative' }}>
            <button 
              onClick={() => setSelectedOrder(null)}
              style={{ position: 'absolute', right: '1.25rem', top: '1.25rem', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
            >
              <X size={20} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <div style={{ background: 'rgba(2, 132, 199, 0.1)', padding: '0.5rem', borderRadius: '10px' }}>
                <UploadCloud color="var(--accent-blue)" size={24} />
              </div>
              <div>
                <h2 style={{ fontSize: '1.35rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Fulfill Lab Order #{selectedOrder.id}</h2>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Patient: <strong>{selectedOrder.patient_name || `Patient #${selectedOrder.patient_id}`}</strong> ({selectedOrder.patient_health_id || 'ID Pending'})
                </div>
              </div>
            </div>

            <div style={{ background: 'var(--bg-tertiary)', padding: '0.85rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
              <strong>Requested Tests:</strong> {selectedOrder.tests.map(t => t.name).join(', ') || 'General Lab Work'}
              {selectedOrder.clinical_notes && (
                <div style={{ marginTop: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  <em>Clinical Notes:</em> {selectedOrder.clinical_notes}
                </div>
              )}
            </div>

            {statusMessage && (
              <div style={{ 
                padding: '0.75rem 1rem', 
                borderRadius: '8px', 
                marginBottom: '1.25rem', 
                fontSize: '0.85rem',
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                background: statusMessage.type === 'error' ? 'rgba(239, 68, 68, 0.1)' : statusMessage.type === 'success' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(2, 132, 199, 0.1)',
                color: statusMessage.type === 'error' ? 'var(--accent-red)' : statusMessage.type === 'success' ? 'var(--accent-green)' : 'var(--accent-blue)'
              }}>
                {statusMessage.type === 'error' ? <AlertCircle size={16} /> : statusMessage.type === 'success' ? <FileCheck size={16} /> : <Clock size={16} />}
                <span>{statusMessage.text}</span>
              </div>
            )}
            
            <form onSubmit={handleCompleteOrder}>
              {/* PDF / File Dropzone */}
              <div style={{ marginBottom: '1.25rem' }}>
                <label className="input-label" style={{ fontWeight: 600, marginBottom: '0.4rem', display: 'block' }}>
                  Laboratory Report Document (PDF, PNG, JPG)
                </label>
                <div 
                  style={{
                    border: '2px dashed var(--border-light)',
                    borderRadius: '10px',
                    padding: '1.5rem',
                    textAlign: 'center',
                    background: uploadFile ? 'rgba(2, 132, 199, 0.03)' : 'var(--bg-secondary)',
                    cursor: 'pointer',
                    transition: 'border-color 0.2s'
                  }}
                  onClick={() => document.getElementById('lab-file-input').click()}
                >
                  <input 
                    id="lab-file-input"
                    type="file" 
                    accept=".pdf,.png,.jpg,.jpeg" 
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  {uploadFile ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
                      <FileCheck color="var(--accent-green)" size={28} />
                      <div style={{ textAlign: 'left' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>{uploadFile.name}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{(uploadFile.size / 1024).toFixed(1)} KB • Ready for automated AI OCR extraction</div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <UploadCloud size={32} color="var(--accent-blue)" style={{ margin: '0 auto 0.5rem auto', display: 'block' }} />
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>Click to select or drag PDF lab report here</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>Supports standard diagnostic PDF reports or scanned lab slips (max 10MB)</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Optional Technician Notes */}
              <div className="input-group" style={{ marginBottom: '1.25rem' }}>
                <label className="input-label">Technician Observations / Verification Remarks</label>
                <input 
                  type="text"
                  className="input-field"
                  placeholder="e.g. Verified by Lab Lead Dr. Sharma, sample hemolyzed check passed"
                  value={technicianNotes}
                  onChange={e => setTechnicianNotes(e.target.value)}
                />
              </div>

              {/* Manual Structured Values (Optional fallback) */}
              <div className="input-group" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <label className="input-label" style={{ margin: 0 }}>Structured Biomarker Values (Optional)</label>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Auto-extracted if PDF uploaded</span>
                </div>
                <textarea 
                  className="input-field" 
                  rows={3}
                  value={resultsData}
                  onChange={e => setResultsData(e.target.value)}
                  placeholder='e.g. {"Hemoglobin": "14.2 g/dL", "Platelets": "240,000 /mcL"}'
                  style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  style={{ flex: 1 }} 
                  onClick={() => setSelectedOrder(null)}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  style={{ flex: 1.5, background: 'var(--accent-blue)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }} 
                  disabled={submitting}
                >
                  {submitting ? 'Ingesting & Completing...' : 'Complete & Attach to Patient'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
