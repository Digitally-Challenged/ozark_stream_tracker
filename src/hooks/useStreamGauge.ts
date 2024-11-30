import { useState, useEffect } from 'react';
import { Stream, GaugeReading } from '../types/stream';

export function useStreamGauge(stream: Stream) {
  const [reading, setReading] = useState<GaugeReading | null>(null);
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

        setReading({
          value: parseFloat(latestReading.value),
          timestamp: latestReading.dateTime
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch gauge data'));
      } finally {
        setLoading(false);
      }
    };

    fetchGaugeData();
    const interval = setInterval(fetchGaugeData, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(interval);
  }, [stream.gauge.id]);

  const currentLevel = reading ? 
    (reading.value < stream.targetLevels.tooLow ? 'X' :
     reading.value < stream.targetLevels.optimal ? 'L' :
     reading.value < stream.targetLevels.high ? 'O' : 'H')
    : 'N/A';

  return {
    currentLevel,
    reading,
    loading,
    error
  };
}