import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, Check, X, Save, RefreshCw, AlertCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function PermissionManager() {
  const [permissions, setPermissions] = useState([]);
  const [rolePermissions, setRolePermissions] = useState({});
  const [selectedRole, setSelectedRole] = useState('Doctor');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const roles = ['Super Admin', 'Hospital Admin', 'Doctor', 'Nurse', 'Receptionist', 'Lab Technician', 'Patient'];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const authHeader = { headers: { Authorization: `Bearer ${token}` } };
      
      const permRes = await axios.get(`${API_BASE}/identity/authorization/permissions`, authHeader).catch(() => ({ data: [] }));
      const roleRes = await axios.get(`${API_BASE}/identity/authorization/role-permissions`, authHeader).catch(() => ({ data: {} }));

      setPermissions(permRes.data.length ? permRes.data : [
        { id: 1, name: 'patient.read', resource: 'patient', action: 'read', description: 'View patient profiles' },
        { id: 2, name: 'record.create', resource: 'record', action: 'create', description: 'Create medical records' },
        { id: 3, name: 'billing.write', resource: 'billing', action: 'write', description: 'Issue invoices & process payments' },
        { id: 4, name: 'audit.read', resource: 'audit', action: 'read', description: 'View and export audit trails' },
      ]);

      setRolePermissions(roleRes.data || {});
    } catch (err) {
      console.error('Failed to load permission data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (permId) => {
    setRolePermissions(prev => {
      const current = prev[selectedRole] || [];
      const updated = current.includes(permId)
        ? current.filter(id => id !== permId)
        : [...current, permId];
      return { ...prev, [selectedRole]: updated };
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_BASE}/identity/authorization/role-permissions`, {
        role: selectedRole,
        permission_ids: rolePermissions[selectedRole] || []
      }, { headers: { Authorization: `Bearer ${token}` } });

      setMessage({ type: 'success', text: `Permissions for ${selectedRole} updated successfully!` });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to update permissions.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-xl">
      <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl">
            <Shield size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold">Dynamic RBAC Permission Manager</h2>
            <p className="text-sm text-slate-400">Manage fine-grained database-backed access permissions per role</p>
          </div>
        </div>
        <button onClick={fetchData} className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition">
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-xl mb-4 flex items-center gap-2 ${message.type === 'success' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}`}>
          <AlertCircle size={18} />
          <span>{message.text}</span>
        </div>
      )}

      {/* Role Selection Bar */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {roles.map(r => (
          <button
            key={r}
            onClick={() => setSelectedRole(r)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition ${selectedRole === r ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Permission Grid */}
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
        {permissions.map(perm => {
          const isAssigned = (rolePermissions[selectedRole] || []).includes(perm.id);
          return (
            <div key={perm.id} className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-xl transition">
              <div>
                <div className="font-semibold text-slate-200">{perm.name}</div>
                <div className="text-xs text-slate-400">{perm.description}</div>
              </div>
              <button
                onClick={() => handleToggle(perm.id)}
                className={`p-2 rounded-lg font-medium transition flex items-center gap-1 text-xs ${isAssigned ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-slate-700/50 text-slate-500 border border-slate-700'}`}
              >
                {isAssigned ? <Check size={16} /> : <X size={16} />}
                <span>{isAssigned ? 'Allowed' : 'Denied'}</span>
              </button>
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-xl transition shadow-lg shadow-indigo-600/30 disabled:opacity-50"
        >
          <Save size={18} />
          <span>{saving ? 'Saving...' : 'Save Role Permissions'}</span>
        </button>
      </div>
    </div>
  );
}
