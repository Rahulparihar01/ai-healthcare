import React, { useState, useEffect } from 'react';

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
}

interface Warning {
  alert_type: string;
  severity: string;
  message: string;
}

interface Props {
  healthId: string;
  proposedMedications: Medication[];
}

const PrescriptionAssistant: React.FC<Props> = ({ healthId, proposedMedications }) => {
  const [warnings, setWarnings] = useState<Warning[]>([]);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    if (proposedMedications.length === 0) {
      setWarnings([]);
      return;
    }

    const checkSafety = async () => {
      setIsChecking(true);
      try {
        const response = await fetch('/api/v1/copilot/check-prescription', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            health_id: healthId,
            proposed_medications: proposedMedications
          })
        });

        if (response.ok) {
          const data = await response.json();
          setWarnings(data);
        }
      } catch (error) {
        console.error("Failed to check prescription", error);
      } finally {
        setIsChecking(false);
      }
    };

    const debounceTimer = setTimeout(checkSafety, 1000);
    return () => clearTimeout(debounceTimer);
  }, [healthId, proposedMedications]);

  if (!isChecking && warnings.length === 0) {
    return null; // Don't show anything if there are no warnings
  }

  return (
    <div className="mt-4 p-4 border rounded-md shadow-sm bg-gray-50 border-gray-200">
      <div className="flex items-center space-x-2 mb-2">
        <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h3 className="text-sm font-semibold text-gray-700">AI Copilot Analysis</h3>
      </div>
      
      {isChecking ? (
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-500"></div>
          <span>Checking safety...</span>
        </div>
      ) : (
        <div className="space-y-2">
          {warnings.map((warning, index) => (
            <div 
              key={index} 
              className={`p-3 rounded text-sm ${
                warning.severity === 'HIGH' ? 'bg-red-100 text-red-800 border border-red-200' :
                warning.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                'bg-blue-100 text-blue-800 border border-blue-200'
              }`}
            >
              <strong>{warning.alert_type}:</strong> {warning.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PrescriptionAssistant;
