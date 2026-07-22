import React, { useState, useEffect } from 'react';
import api from '../api';

const Timeline = ({ healthId }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchTimeline = async () => {
        try {
            const response = await api.get(`/records/list?health_id=${healthId}`);
            setEvents(response.data);
            setError('');
        } catch (err) {
            console.error("Failed to fetch timeline", err);
            setError('Failed to load patient timeline.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (healthId) {
            fetchTimeline();
            const interval = setInterval(fetchTimeline, 5000); // Poll every 5s for updates (Processing status)
            return () => clearInterval(interval);
        }
    }, [healthId]);

    if (loading) return <div className="text-center p-4">Loading timeline...</div>;
    if (error) return <div className="text-red-500 p-4">{error}</div>;
    if (events.length === 0) return <div className="text-gray-500 p-4">No medical history found.</div>;

    const getIcon = (type) => {
        switch (type) {
            case 'Visit': return '🩺';
            case 'Diagnosis': return '📋';
            case 'Prescription': return '💊';
            case 'LabReport': return '🧪';
            case 'Radiology': return '🩻';
            case 'Document': return '📄';
            default: return '📝';
        }
    };

    return (
        <div className="mt-8 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Medical Timeline</h2>
            <div className="relative border-l-4 border-blue-500 ml-4">
                {events.map((event, index) => {
                    const isProcessing = event.title.includes('(Processing)');
                    const needsReview = event.title.includes('(Needs Review)');
                    
                    let bgIconColor = 'bg-blue-100';
                    if (isProcessing) bgIconColor = 'bg-yellow-100 animate-pulse';
                    if (needsReview) bgIconColor = 'bg-orange-100';

                    let cardBorder = 'bg-white border-gray-200';
                    if (isProcessing) cardBorder = 'bg-yellow-50 border-yellow-200';
                    if (needsReview) cardBorder = 'bg-orange-50 border-orange-300';
                    
                    return (
                        <div key={event.id} className="mb-8 ml-6 relative">
                            <span className={`absolute flex items-center justify-center w-10 h-10 rounded-full -left-11 ring-4 ring-white ${bgIconColor}`}>
                                <span className="text-xl">{getIcon(event.event_type)}</span>
                            </span>
                            
                            <div className={`p-5 rounded-lg shadow-md border ${cardBorder}`}>
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                        {isProcessing ? "Processing Document" : (needsReview ? event.title.replace(" (Needs Review)", "") : event.title)}
                                        {isProcessing && (
                                            <span className="text-xs font-bold px-2 py-1 bg-yellow-200 text-yellow-800 rounded-full animate-pulse">
                                                Active
                                            </span>
                                        )}
                                        {needsReview && (
                                            <span className="text-xs font-bold px-2 py-1 bg-orange-200 text-orange-800 rounded-full">
                                                Manual Review Required
                                            </span>
                                        )}
                                    </h3>
                                    <span className="text-sm text-gray-500">
                                        {new Date(event.event_date).toLocaleString()}
                                    </span>
                                </div>
                                <div className="text-gray-700 mt-2">
                                    {isProcessing ? (
                                        <div className="flex items-center gap-3">
                                            <svg className="animate-spin h-5 w-5 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            <span className="font-medium text-yellow-800">{event.summary}</span>
                                        </div>
                                    ) : (
                                        event.summary
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Timeline;
