import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Search, Users, FlaskConical, AlertTriangle, Settings, 
  Stethoscope, ScanLine, MoreHorizontal, ChevronRight
} from 'lucide-react';

export default function DoctorDashboard() {
  const { user, logout } = useAuth();
  // Using static data to match the screenshot precisely for this UI layout task
  const [activeTab, setActiveTab] = useState('search');

  return (
    <div className="app-container" style={{ backgroundColor: 'var(--bg-primary)' }}>
      
      {/* Sidebar */}
      <div className="sidebar-light">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 1rem', marginBottom: '2rem' }}>
          <Stethoscope color="var(--accent-blue)" size={28} />
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>HealthID AI</h2>
        </div>
        
        <div style={{ padding: '0 1rem', marginBottom: '2rem', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Welcome back,<br/>
          <strong style={{ color: 'var(--text-primary)', fontSize: '1.1rem' }}>Dr. {user?.username || 'Raj'}</strong>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div 
            className={`nav-item ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search size={20} />
            Search patient
          </div>
          <div 
            className={`nav-item ${activeTab === 'patients' ? 'active' : ''}`}
            onClick={() => setActiveTab('patients')}
          >
            <Users size={20} />
            My patients
          </div>
          <div 
            className={`nav-item ${activeTab === 'labs' ? 'active' : ''}`}
            onClick={() => setActiveTab('labs')}
          >
            <FlaskConical size={20} />
            Lab reports
          </div>
          <div 
            className={`nav-item ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <AlertTriangle size={20} />
            Alerts
          </div>
          <div 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings size={20} />
            Settings
          </div>
        </div>
        
        <div style={{ marginTop: 'auto', padding: '0 1rem' }}>
          <button className="btn btn-secondary" onClick={logout} style={{ width: '100%' }}>Logout</button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content" style={{ backgroundColor: 'var(--bg-primary)', padding: '3rem 4rem' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 600, color: '#000', marginBottom: '0.25rem' }}>
              Doctor portal
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
              Search a patient by health ID or scan their QR code<br/>to pull up their AI summary.
            </p>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.5rem', borderRadius: '50%', background: 'white' }}>
            <MoreHorizontal size={24} color="var(--text-tertiary)" />
          </button>
        </div>

        {/* Actions Row */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2.5rem' }}>
          <div style={{ position: 'relative', width: '250px' }}>
            <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
            <input 
              type="text" 
              className="input-field" 
              style={{ paddingLeft: '2.75rem', height: '100%', margin: 0 }}
              placeholder="Enter ID..."
            />
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem', fontWeight: 500 }}>
            <ScanLine size={18} />
            Scan QR
          </button>
          <button className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', fontWeight: 500, background: '#2563eb' }}>
            Search patient
          </button>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '3rem' }}>
          <div className="glass-panel" style={{ padding: '1.5rem 1.5rem 2rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', fontWeight: 500, marginBottom: '0.75rem', lineHeight: 1.3 }}>
              Patients<br/>today
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 600, color: '#000', lineHeight: 1 }}>18</div>
          </div>
          <div className="glass-panel" style={{ padding: '1.5rem 1.5rem 2rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', fontWeight: 500, marginBottom: '0.75rem', lineHeight: 1.3 }}>
              Pending<br/>lab syncs
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 600, color: '#000', lineHeight: 1 }}>3</div>
          </div>
          <div className="glass-panel" style={{ padding: '1.5rem 1.5rem 2rem 1.5rem', border: 'none', background: 'white', borderRadius: '16px' }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', fontWeight: 500, marginBottom: '0.75rem', lineHeight: 1.3 }}>
              Active<br/>alerts
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 600, color: 'var(--accent-red)', lineHeight: 1 }}>2</div>
          </div>
        </div>

        {/* Recent Searches */}
        <div>
          <h3 style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', fontWeight: 500, marginBottom: '1rem' }}>
            Recent searches
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            
            {/* Card 1 */}
            <div className="glass-panel hover-card" style={{ display: 'flex', alignItems: 'center', padding: '1.25rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', cursor: 'pointer' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '24px', background: 'var(--accent-blue-light)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '1.1rem', marginRight: '1rem' }}>
                RS
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, color: '#000', fontSize: '1.05rem' }}>Ramesh Sahu</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>21-4921-2918-0912</div>
              </div>
              <div className="badge-alert" style={{ marginRight: '1rem', padding: '0.35rem 0.85rem' }}>
                Allergy alert
              </div>
              <ChevronRight color="var(--text-tertiary)" size={20} />
            </div>

            {/* Card 2 */}
            <div className="glass-panel hover-card" style={{ display: 'flex', alignItems: 'center', padding: '1.25rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', cursor: 'pointer' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '24px', background: 'var(--accent-blue-light)', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '1.1rem', marginRight: '1rem' }}>
                SV
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, color: '#000', fontSize: '1.05rem' }}>Sunita Verma</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>21-3810-7742-0455</div>
              </div>
              <ChevronRight color="var(--text-tertiary)" size={20} />
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
