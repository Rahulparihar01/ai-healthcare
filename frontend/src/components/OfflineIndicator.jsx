import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi, RefreshCw } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export function enqueueOfflineRequest(request) {
  const queue = JSON.parse(localStorage.getItem('healthid_offline_queue') || '[]');
  queue.push({
    ...request,
    queuedAt: new Date().toISOString()
  });
  localStorage.setItem('healthid_offline_queue', JSON.stringify(queue));
}

export function getOfflineQueue() {
  return JSON.parse(localStorage.getItem('healthid_offline_queue') || '[]');
}

export async function replayOfflineQueue(apiCaller) {
  const queue = getOfflineQueue();
  if (queue.length === 0) return 0;

  let syncedCount = 0;
  const remainingQueue = [];

  for (const item of queue) {
    try {
      if (apiCaller) {
        await apiCaller(item);
      }
      syncedCount++;
    } catch (err) {
      console.warn("Failed to sync offline item:", item, err);
      remainingQueue.push(item);
    }
  }

  localStorage.setItem('healthid_offline_queue', JSON.stringify(remainingQueue));
  return syncedCount;
}

export default function OfflineIndicator() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [syncing, setSyncing] = useState(false);
  const [queuedCount, setQueuedCount] = useState(0);
  const { t } = useLanguage ? useLanguage() : { t: (k) => k };

  const updateQueueCount = () => {
    setQueuedCount(getOfflineQueue().length);
  };

  useEffect(() => {
    updateQueueCount();

    const handleOnline = async () => {
      setIsOffline(false);
      setSyncing(true);
      await replayOfflineQueue();
      updateQueueCount();
      setSyncing(false);
    };

    const handleOffline = () => {
      setIsOffline(true);
      updateQueueCount();
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOffline && queuedCount === 0 && !syncing) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 9999,
      background: isOffline ? 'rgba(217, 119, 6, 0.95)' : 'rgba(16, 185, 129, 0.95)',
      color: '#fff',
      padding: '0.5rem 1rem',
      fontSize: '0.875rem',
      fontWeight: 600,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    }}>
      {isOffline ? (
        <>
          <WifiOff style={{ width: '16px', height: '16px' }} />
          <span>{t('offlineMessage') || "Offline Mode Active — Changes queued locally"} ({queuedCount} pending)</span>
        </>
      ) : syncing ? (
        <>
          <RefreshCw style={{ width: '16px', height: '16px' }} className="spin" />
          <span>Syncing offline records to server...</span>
        </>
      ) : (
        <>
          <Wifi style={{ width: '16px', height: '16px' }} />
          <span>Back online — All records synced!</span>
        </>
      )}
    </div>
  );
}
