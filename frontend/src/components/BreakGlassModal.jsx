import React, { useState } from 'react';
import axios from 'axios';
import { AlertTriangle, ShieldAlert, Lock, X } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function BreakGlassModal({ patientId, healthId, onClose, onSuccess }) {
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) {
      setError('A valid medical emergency justification is required.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE}/patient/emergency-access`, {
        patient_id: patientId,
        health_id: healthId,
        reason: reason
      }, { headers: { Authorization: `Bearer ${token}` } });

      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to request emergency access.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-rose-500/40 rounded-3xl max-w-md w-full p-6 text-white shadow-2xl relative">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded-full">
          <X size={18} />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-rose-500/20 text-rose-400 rounded-2xl border border-rose-500/30">
            <ShieldAlert size={28} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-rose-400">Emergency Access ("Break-Glass")</h2>
            <p className="text-xs text-slate-400">Time-limited emergency clinical record access</p>
          </div>
        </div>

        <div className="p-3 bg-rose-950/40 border border-rose-500/30 rounded-xl mb-4 text-xs text-rose-300 leading-relaxed">
          <strong>WARNING:</strong> Break-Glass access overrides patient privacy restrictions. Every action will be permanently logged in the audit trail for compliance review.
        </div>

        {error && (
          <div className="p-3 bg-rose-500/20 text-rose-300 rounded-xl mb-4 text-xs border border-rose-500/40">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Clinical Justification / Emergency Reason *</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., Unconscious trauma patient in ER requiring immediate medical history access."
              rows={3}
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-rose-500"
            />
          </div>

          <div className="flex gap-3">
            <button type="button" onClick={onClose} className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2.5 rounded-xl text-sm font-medium transition">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-rose-600 hover:bg-rose-500 text-white py-2.5 rounded-xl text-sm font-semibold transition shadow-lg shadow-rose-600/30 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Authorize Access'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
