import React, { useState } from 'react';
import { HelpCircle, Loader, AlertTriangle } from 'lucide-react';
import api from '../../api';

interface AbnormalLabExplainerProps {
  biomarker: string;
  value: string | number;
  healthId?: string;
}

const AbnormalLabExplainer: React.FC<AbnormalLabExplainerProps> = ({ biomarker, value, healthId }) => {
  const [explanation, setExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchExplanation = async () => {
    if (explanation) {
      setIsOpen(!isOpen);
      return;
    }
    
    setLoading(true);
    setIsOpen(true);
    setError(null);
    try {
      const response = await api.get('/copilot/explain-lab', {
        params: { biomarker, value, health_id: healthId }
      });
      setExplanation(response.data.explanation);
    } catch (err) {
      console.error(err);
      setError('Failed to load explanation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative inline-block ml-2">
      <button 
        onClick={fetchExplanation}
        className="text-blue-500 hover:text-blue-700 transition-colors p-1 rounded-full hover:bg-blue-50"
        title="Explain this value"
      >
        <HelpCircle size={16} />
      </button>

      {isOpen && (
        <div className="absolute z-50 left-full ml-2 top-1/2 -translate-y-1/2 w-64 bg-white border border-gray-200 shadow-xl rounded-lg p-3 text-sm">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-semibold text-gray-800 flex items-center gap-1">
              <AlertTriangle size={14} className="text-amber-500" /> AI Insight
            </h4>
            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
          </div>
          
          {loading ? (
            <div className="flex items-center justify-center p-4 text-blue-500">
              <Loader className="animate-spin" size={20} />
            </div>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <p className="text-gray-600 leading-relaxed">{explanation}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AbnormalLabExplainer;
