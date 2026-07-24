import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Microscope, CheckCircle, FileText, Search } from 'lucide-react';
import api from '../api';

export default function LabTechnicianDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('pending');
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Results upload state
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [resultsData, setResultsData] = useState('');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const res = await api.get('/labs/pending');
      setOrders(res.data);
    } catch (error) {
      console.error("Failed to fetch pending lab orders", error);
    }
  };

  const handleCompleteOrder = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let resultsJson = {};
      try {
        resultsJson = JSON.parse(resultsData);
      } catch (err) {
        resultsJson = { summary: resultsData };
      }
      
      await api.post(`/labs/orders/${selectedOrder.id}/complete`, { results: resultsJson });
      alert("Lab order completed successfully");
      setSelectedOrder(null);
      setResultsData('');
      fetchOrders();
    } catch (error) {
      alert("Failed to complete order: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Microscope color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Lab Portal</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>{user?.username}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div className={`nav-item ${activeTab === 'pending' ? 'active' : ''}`} onClick={() => setActiveTab('pending')}>
            <FileText size={20} />
            Pending Orders
          </div>
          <div className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
            <Search size={20} />
            Search History
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        
        {activeTab === 'pending' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
                  Pending Lab Orders
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
                  Review and fulfill test requests from doctors.
                </p>
              </div>
            </div>

            <div className="glass-panel" style={{ background: 'white', padding: '0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Order ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Patient ID</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Requested Tests</th>
                    <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.length === 0 && (
                    <tr><td colSpan="4" style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-tertiary)' }}>No pending orders found.</td></tr>
                  )}
                  {orders.map(order => (
                    <tr key={order.id} style={{ borderTop: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--accent-blue)', fontWeight: 500 }}>{order.id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500, color: '#000' }}>{order.patient_id}</td>
                      <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>
                        {order.tests.map(t => t.name).join(', ') || 'Unknown'}
                      </td>
                      <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                        <button className="btn btn-primary" style={{ padding: '0.4rem 1rem' }} onClick={() => setSelectedOrder(order)}>
                          Upload Results
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {activeTab === 'history' && (
          <div className="glass-panel" style={{ background: 'white', padding: '4rem', textAlign: 'center', color: 'var(--text-tertiary)' }}>
            Search functionality for completed orders will be implemented in future phases.
          </div>
        )}
      </div>

      {/* Upload Results Modal */}
      {selectedOrder && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ background: 'white', padding: '2.5rem', width: '550px', borderRadius: '16px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#000' }}>Upload Lab Results</h2>
            <div style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
              <strong>Order ID:</strong> {selectedOrder.id} <br/>
              <strong>Tests:</strong> {selectedOrder.tests.map(t => t.name).join(', ')}
            </div>
            
            <form onSubmit={handleCompleteOrder}>
              <div className="input-group" style={{ marginBottom: '1.5rem' }}>
                <label className="input-label">Results (JSON or Text format)</label>
                <textarea 
                  className="input-field" 
                  rows={6}
                  value={resultsData}
                  onChange={e => setResultsData(e.target.value)}
                  placeholder='{"WBC": "6.5", "RBC": "4.8"}'
                  required
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setSelectedOrder(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1, background: 'var(--accent-blue)' }} disabled={loading}>
                  {loading ? 'Submitting...' : 'Complete Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
