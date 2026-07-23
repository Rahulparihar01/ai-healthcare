import React, { useEffect, useState } from 'react';

interface TimelineEvent {
  id: number;
  event_type: string;
  reference_id: number;
  event_date: string;
  title: string;
  summary: string;
}

const MedicalTimeline: React.FC<{ healthId: string }> = ({ healthId }) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [diseaseKeyword, setDiseaseKeyword] = useState('');

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const queryParam = diseaseKeyword ? `?disease_keyword=${encodeURIComponent(diseaseKeyword)}` : '';
        const response = await fetch(`/api/v1/timeline/${healthId}${queryParam}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (response.ok) {
          const data = await response.json();
          setEvents(data);
        }
      } catch (err) {
        console.error("Failed to fetch timeline", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, [healthId, diseaseKeyword]);

  if (loading) return <div>Loading timeline...</div>;
  if (events.length === 0) return <div>No timeline events found.</div>;

  return (
    <div>
      <div className="mb-6 flex gap-2 items-center max-w-sm">
        <input 
          type="text" 
          placeholder="Filter by disease or keyword..." 
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={diseaseKeyword}
          onChange={(e) => setDiseaseKeyword(e.target.value)}
        />
      </div>
      <div className="relative border-l border-gray-200 ml-3">
        {events.map((event, index) => (
        <div key={event.id} className="mb-8 ml-6">
          <span className="absolute flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full -left-3 ring-8 ring-white">
            <svg className="w-3 h-3 text-blue-800" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
            </svg>
          </span>
          <h3 className="flex items-center mb-1 text-lg font-semibold text-gray-900">
            {event.title} 
            <span className="bg-blue-100 text-blue-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded ml-3">
              {event.event_type}
            </span>
          </h3>
          <time className="block mb-2 text-sm font-normal leading-none text-gray-400">
            {new Date(event.event_date).toLocaleString()}
          </time>
          <p className="mb-4 text-base font-normal text-gray-500 whitespace-pre-wrap">{event.summary}</p>
        </div>
      ))}
      </div>
    </div>
  );
};

export default MedicalTimeline;
