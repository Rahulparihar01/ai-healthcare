import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity } from 'lucide-react';
import api from '../api';

export default function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('Doctor');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/identity/auth/register', {
        username,
        password,
        email,
        role
      });
      // Route to OTP Verification after successful registration
      navigate('/verify-otp', { state: { email } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Username or email might be taken.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-panel animate-in" style={{ width: '100%', maxWidth: '420px', padding: '2.5rem' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Activity size={48} color="var(--accent-purple)" style={{ marginBottom: '1rem' }} />
          <h2>Join <span className="text-gradient">HealthID AI</span></h2>
          <p style={{ color: 'var(--text-secondary)' }}>Create your clinic account</p>
        </div>

        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.1)', color: 'var(--accent-rose)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.9rem', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Role</label>
            <select 
              className="input-field" 
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="Doctor">Doctor</option>
              <option value="Receptionist">Receptionist</option>
              <option value="Lab Technician">Lab Technician</option>
              <option value="Hospital Admin">Hospital Admin</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Email</label>
            <input 
              type="email" 
              className="input-field" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
              placeholder="dr.smith@hospital.com"
            />
          </div>

          <div className="input-group">
            <label className="input-label">Username</label>
            <input 
              type="text" 
              className="input-field" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required 
              placeholder="dr_smith"
            />
          </div>
          
          <div className="input-group">
            <label className="input-label">Password</label>
            <input 
              type="password" 
              className="input-field" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>
        
        <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.9rem', color: 'var(--text-tertiary)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-blue)', textDecoration: 'none' }}>Sign In here</Link>
        </div>
      </div>
    </div>
  );
}
