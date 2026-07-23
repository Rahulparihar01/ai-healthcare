import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BiomarkerResult {
  id: number;
  biomarker_name: string;
  value: string;
  unit: string;
  recorded_at: string;
}

interface Props {
  healthId: string;
  biomarker: string;
}

const BiomarkerTrendChart: React.FC<Props> = ({ healthId, biomarker }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/v1/timeline/${healthId}/biomarkers?biomarker=${encodeURIComponent(biomarker)}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (response.ok) {
          const results: BiomarkerResult[] = await response.json();
          // Format data for Recharts
          const chartData = results.map(r => ({
            date: new Date(r.recorded_at).toLocaleDateString(),
            value: parseFloat(r.value),
            unit: r.unit
          }));
          setData(chartData);
        }
      } catch (err) {
        console.error("Failed to fetch biomarker data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [healthId, biomarker]);

  if (loading) return <div>Loading chart...</div>;
  if (data.length === 0) return <div>No data available for {biomarker}.</div>;

  return (
    <div className="w-full h-72 p-4 bg-white rounded-lg shadow border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{biomarker} Trend</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={3} dot={{ r: 5 }} activeDot={{ r: 8 }} />
          <CartesianGrid stroke="#ccc" strokeDasharray="5 5" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 12 }} />
          <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            formatter={(value: number) => [`${value} ${data[0]?.unit}`, biomarker]} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BiomarkerTrendChart;
