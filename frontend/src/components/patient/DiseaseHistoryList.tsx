import React from 'react';

interface Disease {
  id: number;
  disease_name: string;
  status: string;
  severity: string;
}

interface DiseaseHistoryListProps {
  diseases: Disease[];
}

export const DiseaseHistoryList: React.FC<DiseaseHistoryListProps> = ({ diseases }) => {
  if (!diseases || diseases.length === 0) {
    return <p className="text-gray-500">No known chronic diseases.</p>;
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-3 border-b pb-2">Disease History</h3>
      <ul className="space-y-2">
        {diseases.map((disease) => (
          <li key={disease.id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
            <div>
              <span className="font-medium text-gray-800">{disease.disease_name}</span>
              <span className="ml-2 text-xs bg-blue-100 text-blue-800 py-1 px-2 rounded-full">{disease.status}</span>
            </div>
            {disease.severity && (
              <span className={`text-xs px-2 py-1 rounded ${disease.severity.toLowerCase() === 'severe' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                {disease.severity}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
