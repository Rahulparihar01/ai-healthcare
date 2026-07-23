import React, { useEffect, useState } from 'react';

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  message: string;
  created_at: string;
}

const NotificationCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchAlerts(); // Initial fetch
    
    const token = localStorage.getItem('token');
    if (!token) return;

    // Use ws:// or wss:// based on current protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Vite proxies /api so we might need to connect directly to the backend host or rely on Vite's WS proxy
    const ws = new WebSocket(`ws://localhost:8000/api/v1/alerts/ws?token=${token}`);

    ws.onmessage = (event) => {
      // In a real scenario, the backend might send JSON with the new alert
      // For now, if we get a ping/message, we just refetch
      fetchAlerts();
    };

    return () => {
      ws.close();
    };
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/v1/alerts', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error("Failed to fetch alerts", error);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await fetch(`/api/v1/alerts/${id}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      setAlerts(alerts.filter(a => a.id !== id));
    } catch (error) {
      console.error("Failed to mark read", error);
    }
  };

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-800 focus:outline-none"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {alerts.length > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {alerts.length}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 w-80 mt-2 bg-white rounded-md shadow-lg overflow-hidden z-20 border border-gray-200">
          <div className="py-2 bg-gray-50 border-b border-gray-200 px-4">
            <h3 className="text-sm font-semibold text-gray-700">Notifications</h3>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {alerts.length === 0 ? (
              <div className="px-4 py-3 text-sm text-gray-500 text-center">No new alerts</div>
            ) : (
              alerts.map(alert => (
                <div key={alert.id} className={`px-4 py-3 border-b border-gray-100 ${alert.severity === 'HIGH' ? 'bg-red-50' : alert.severity === 'MEDIUM' ? 'bg-yellow-50' : ''}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{alert.alert_type}</p>
                      <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                    </div>
                    <button onClick={() => markAsRead(alert.id)} className="text-xs text-blue-500 hover:text-blue-700">
                      Mark Read
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
