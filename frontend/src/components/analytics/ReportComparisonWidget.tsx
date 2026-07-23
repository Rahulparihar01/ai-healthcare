import React, { useState } from 'react';

interface Props {
  documentAId: number;
  documentBId: number;
}

const ReportComparisonWidget: React.FC<Props> = ({ documentAId, documentBId }) => {
  const [comparison, setComparison] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/records/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          doc1_id: documentAId,
          doc2_id: documentBId
        })
      });

      if (response.ok) {
        const data = await response.json();
        setComparison(data.comparison);
      } else {
        const errData = await response.json();
        setError(errData.detail || "Failed to compare reports.");
      }
    } catch (err) {
      console.error(err);
      setError("An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">AI Report Comparison</h3>
        <button 
          onClick={handleCompare}
          disabled={loading || !documentAId || !documentBId}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Compare Selected Reports'}
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded mb-4">
          {error}
        </div>
      )}

      {comparison && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded">
          <h4 className="font-semibold text-gray-700 mb-2">Key Differences & Progress:</h4>
          <div className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">
            {comparison}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportComparisonWidget;
