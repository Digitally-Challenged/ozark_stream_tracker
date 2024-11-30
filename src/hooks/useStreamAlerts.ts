import { useMemo } from 'react';
import { StreamData } from '../types/stream';
import { useStreamGauge } from './useStreamGauge';

export interface StreamAlert {
  type: 'high' | 'low' | 'error';
  stream: StreamData;
  message: string;
  severity: 'warning' | 'error' | 'info';
  timestamp: Date;
}

export function useStreamAlerts(stream: StreamData) {
  const { currentLevel, error, reading } = useStreamGauge(stream);
  
  const alert = useMemo(() => {
    if (error) {
      return {
        type: 'error' as const,
        stream,
        message: `Unable to fetch gauge data for ${stream.name}`,
        severity: 'error' as const,
        timestamp: new Date()
      };
    }
    
    if (reading) {
      if (currentLevel === 'H') {
        return {
          type: 'high' as const,
          stream,
          message: `${stream.name} is running high (${reading.value.toFixed(2)} ft) - Use caution`,
          severity: 'warning' as const,
          timestamp: new Date(reading.timestamp)
        };
      }
      
      if (currentLevel === 'X') {
        return {
          type: 'low' as const,
          stream,
          message: `${stream.name} is too low for paddling (${reading.value.toFixed(2)} ft)`,
          severity: 'info' as const,
          timestamp: new Date(reading.timestamp)
        };
      }
    }
    
    return null;
  }, [currentLevel, error, reading, stream]);

  return alert;
}

export function useAllStreamAlerts(streams: StreamData[]) {
  const alerts = streams.map(stream => useStreamAlerts(stream)).filter((alert): alert is StreamAlert => alert !== null);
  
  const sortedAlerts = useMemo(() => 
    [...alerts].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime()),
    [alerts]
  );

  const stats = useMemo(() => ({
    total: sortedAlerts.length,
    highWater: sortedAlerts.filter(a => a.type === 'high').length,
    tooLow: sortedAlerts.filter(a => a.type === 'low').length,
    errors: sortedAlerts.filter(a => a.type === 'error').length
  }), [sortedAlerts]);

  return { alerts: sortedAlerts, stats };
}