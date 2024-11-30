import { useState, useEffect } from 'react';
import { Stream, GaugeReading, LevelTrend } from '../types/stream';

export function useStreamGauge(stream: Stream) {
  const [reading, setReading] = useState<GaugeReading | null>(null);
  const [previousReading, setPreviousReading] = useState<GaugeReading | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchGaugeData = async () => {
      if (!stream.gauge.id) {
        setError(new Error('No gauge ID provided'));
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(
          `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=${stream.gauge.id}&parameterCd=00065`,
          {
            headers: {
              'Accept': 'application/json'
            }
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const latestReading = data.value.timeSeries[0].values[0].value[0];
        
        setReading(prevReading => {
          setPreviousReading(prevReading);
          return {
            value: parseFloat(latestReading.value),
            timestamp: latestReading.dateTime
          };
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch gauge data'));
      } finally {
        setLoading(false);
      }
    };

    fetchGaugeData();
    const interval = setInterval(fetchGaugeData, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, [stream.gauge.id]);

  const determineTrend = (): LevelTrend => {
    if (!reading || !previousReading) return LevelTrend.None;
    
    const difference = reading.value - previousReading.value;
    const THRESHOLD = 0.1; // Minimum change to consider rising/falling
    
    if (Math.abs(difference) < THRESHOLD) return LevelTrend.Holding;
    return difference > 0 ? LevelTrend.Rising : LevelTrend.Falling;
  };

  const currentLevel = reading ? {
    status: reading.value < stream.targetLevels.tooLow ? 'X' :
            reading.value < stream.targetLevels.optimal ? 'L' :
            reading.value < stream.targetLevels.high ? 'O' : 'H',
    trend: determineTrend()
  } : undefined;

  return {
    currentLevel,
    reading,
    loading,
    error
  };
}