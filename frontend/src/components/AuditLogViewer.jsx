import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldCheck, Download, RefreshCw, FileText, Filter } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function AuditLogViewer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const url = actionFilter ? `${API_BASE}/audit/logs?action=${actionFilter}` : `${API_BASE}/audit/logs`;
      const res = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: [] }));
      setLogs(res.data || []);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    const token = localStorage.getItem('token');
    window.open(`${API_BASE}/audit/export?format=${format}&token=${token}`, '_blank');
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold">System Audit Trail & Compliance Log</h2>
            <p className="text-sm text-slate-400">HIPAA & GDPR immutable request audit logs</p>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center gap-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 px-3 py-2 rounded-xl text-xs font-semibold transition"
          >
            <Download size={14} />
            <span>Export CSV</span>
          </button>
          <button
            onClick={fetchLogs}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <Filter size={16} className="text-slate-400" />
        <input
          type="text"
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          placeholder="Filter by action (e.g., GET /records, LOGIN)..."
          className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 w-full sm:w-72"
        />
      </div>

      <div className="overflow-x-auto max-h-96 overflow-y-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] sticky top-0">
            <tr>
              <th className="p-3">ID</th>
              <th className="p-3">User ID</th>
              <th className="p-3">Action</th>
              <th className="p-3">IP Address</th>
              <th className="p-3">Status</th>
              <th className="p-3">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-mono text-slate-400">#{log.id}</td>
                <td className="p-3">{log.user_id || 'System'}</td>
                <td className="p-3 font-medium text-slate-200">{log.action}</td>
                <td className="p-3 font-mono text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${log.status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    {log.status}
                  </span>
                </td>
                <td className="p-3 text-slate-400">{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
