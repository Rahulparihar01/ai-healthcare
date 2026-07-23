import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import api from '../../api';
import { Loader, AlertCircle } from 'lucide-react';

const PopulationDashboard: React.FC = () => {
  const [diseaseData, setDiseaseData] = useState<any[]>([]);
  const [highRiskPatients, setHighRiskPatients] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [readmissions, setReadmissions] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [diseaseRes, riskRes, statsRes, readmissionsRes] = await Promise.all([
          api.get('/analytics/disease-prevalence'),
          api.get('/analytics/high-risk-patients'),
          api.get('/analytics/processing-stats'),
          api.get('/analytics/readmissions')
        ]);
        setDiseaseData(diseaseRes.data);
        setHighRiskPatients(riskRes.data);
        setStats(statsRes.data);
        setReadmissions(readmissionsRes.data);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="animate-spin text-blue-600" size={32} />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-8">Population Health Analytics</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-500 mb-1">OCR Accuracy</p>
          <p className="text-2xl font-bold text-gray-900">{stats.ocr_accuracy || 'N/A'}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-500 mb-1">Processing Time</p>
          <p className="text-2xl font-bold text-gray-900">{stats.avg_document_processing_time || 'N/A'}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-500 mb-1">30-Day Readmission</p>
          <div className="flex items-end gap-2">
            <p className="text-2xl font-bold text-gray-900">{readmissions['30_day_readmission_rate'] || 'N/A'}</p>
            <p className="text-sm font-medium text-green-600 mb-1">{readmissions.trend}</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <p className="text-sm font-medium text-gray-500 mb-1">Total Docs Processed</p>
          <p className="text-2xl font-bold text-gray-900">{stats.total_documents_processed || 'N/A'}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Disease Prevalence (Top 10)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={diseaseData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} tick={{fontSize: 12}} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <AlertCircle className="text-red-500" size={20} />
            High-Risk Patients (&gt;3 Chronic Conditions)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-500">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">Health ID</th>
                  <th className="px-4 py-3">Gender</th>
                  <th className="px-4 py-3">Chronic Count</th>
                </tr>
              </thead>
              <tbody>
                {highRiskPatients.length === 0 ? (
                  <tr><td colSpan={3} className="px-4 py-4 text-center">No high risk patients found.</td></tr>
                ) : (
                  highRiskPatients.map((p, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3 font-medium text-gray-900">{p.health_id}</td>
                      <td className="px-4 py-3">{p.gender}</td>
                      <td className="px-4 py-3">
                        <span className="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                          {p.chronic_diseases_count}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PopulationDashboard;
