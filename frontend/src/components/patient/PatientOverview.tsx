import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { DiseaseHistoryList } from './DiseaseHistoryList';
import { AllergyList } from './AllergyList';

interface PatientOverviewProps {
  healthId: string;
}

export const PatientOverview: React.FC<PatientOverviewProps> = ({ healthId }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`/api/v1/patients/${healthId}/health-summary`);
        setData(response.data);
      } catch (err: any) {
        setError('Failed to fetch patient summary');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [healthId]);

  if (loading) return <div className="p-4 text-center">Loading patient data...</div>;
  if (error) return <div className="p-4 text-red-500 text-center">{error}</div>;
  if (!data) return null;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white p-6 rounded-lg shadow-lg mb-6 border-l-4 border-blue-500">
        <h2 className="text-2xl font-bold text-gray-800">{data.full_name}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm text-gray-600">
          <div>
            <span className="block text-xs text-gray-400 uppercase">Health ID</span>
            <span className="font-semibold">{data.health_id}</span>
          </div>
          <div>
            <span className="block text-xs text-gray-400 uppercase">DOB</span>
            <span className="font-semibold">{data.dob || 'N/A'}</span>
          </div>
          <div>
            <span className="block text-xs text-gray-400 uppercase">Gender</span>
            <span className="font-semibold">{data.gender || 'N/A'}</span>
          </div>
          <div>
            <span className="block text-xs text-gray-400 uppercase">Blood Group</span>
            <span className="font-semibold text-red-500">{data.blood_group || 'N/A'}</span>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <DiseaseHistoryList diseases={data.diseases} />
          <AllergyList allergies={data.allergies} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-3 border-b pb-2">Recent Lab Results</h3>
          {data.recent_lab_results?.length > 0 ? (
            <ul className="space-y-3">
              {data.recent_lab_results.map((lab: any) => (
                <li key={lab.id} className="p-3 bg-gray-50 rounded">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-gray-800">{lab.biomarker_name}</span>
                    <span className="text-xs text-gray-500">{new Date(lab.recorded_at).toLocaleDateString()}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-xl font-bold">{lab.value}</span>
                    <span className="ml-1 text-gray-500">{lab.unit}</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">Ref: {lab.reference_range}</div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No recent lab results.</p>
          )}
        </div>
      </div>
    </div>
  );
};
