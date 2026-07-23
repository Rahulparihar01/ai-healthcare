import React from 'react';

interface Allergy {
  id: number;
  allergen: string;
  severity: string;
  reaction: string;
}

interface AllergyListProps {
  allergies: Allergy[];
}

export const AllergyList: React.FC<AllergyListProps> = ({ allergies }) => {
  if (!allergies || allergies.length === 0) {
    return <p className="text-gray-500">No known allergies.</p>;
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow mt-4">
      <h3 className="text-lg font-semibold mb-3 border-b pb-2 text-red-700">Allergies</h3>
      <ul className="space-y-2">
        {allergies.map((allergy) => (
          <li key={allergy.id} className="flex justify-between items-center p-2 bg-red-50 rounded border border-red-100">
            <div>
              <span className="font-semibold text-red-900">{allergy.allergen}</span>
              {allergy.reaction && <p className="text-sm text-red-700 mt-1">Reaction: {allergy.reaction}</p>}
            </div>
            {allergy.severity && (
              <span className={`text-xs px-2 py-1 rounded font-bold uppercase ${allergy.severity.toLowerCase() === 'severe' ? 'bg-red-500 text-white' : 'bg-orange-200 text-orange-900'}`}>
                {allergy.severity}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
