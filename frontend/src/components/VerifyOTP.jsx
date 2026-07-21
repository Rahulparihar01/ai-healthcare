import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Activity } from 'lucide-react';
import api from '../api';

export default function VerifyOTP() {
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/auth/verify-otp', {
        email: email,
        otp_code: otpCode
      });
      alert('Email verified successfully! You can now log in.');
      navigate('/login');
    } catch (err) {
      setError('Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  if (!email) {
    return <div className="app-container" style={{justifyContent: 'center', alignItems: 'center'}}>
      <p>No email provided for verification. Please <a href="/register" style={{color: 'var(--accent-blue)'}}>register</a> first.</p>
    </div>;
  }

  return (
    <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-panel animate-in" style={{ width: '100%', maxWidth: '420px', padding: '2.5rem' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Activity size={48} color="var(--accent-emerald)" style={{ marginBottom: '1rem' }} />
          <h2>Verify <span className="text-gradient">Your Email</span></h2>
          <p style={{ color: 'var(--text-secondary)' }}>We sent a 6-digit code to <strong>{email}</strong></p>
        </div>

        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.1)', color: 'var(--accent-rose)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.9rem', border: '1px solid rgba(244, 63, 94, 0.2)' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">6-Digit OTP Code</label>
            <input 
              type="text" 
              className="input-field" 
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              required 
              placeholder="123456"
              maxLength={6}
              style={{ textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5rem' }}
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Verifying...' : 'Verify Email'}
          </button>
        </form>
      </div>
    </div>
  );
}
