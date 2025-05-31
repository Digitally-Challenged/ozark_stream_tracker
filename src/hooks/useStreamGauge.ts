// src/hooks/useStreamGauge.ts
import { useState, useEffect } from 'react';
import {
  StreamData,
  GaugeReading,
  LevelStatus,
  LevelTrend,
} from '../types/stream';
import { determineLevel, determineTrend } from '../utils/streamLevels';

interface GaugeState {
  currentLevel?: {
    status: LevelStatus;
    trend: LevelTrend;
  };
  reading: GaugeReading | null;
  loading: boolean;
  error: Error | null;
}

export function useStreamGauge(stream: StreamData) {
  const [state, setState] = useState<GaugeState>({
    reading: null,
    loading: true,
    error: null,
  });
  const [previousReading, setPreviousReading] = useState<GaugeReading | null>(
    null
  );

  useEffect(() => {
    let mounted = true;
    const controller = new AbortController();

    const fetchGaugeData = async () => {
      if (!stream.gauge.id) {
        setState((prev) => ({
          ...prev,
          error: new Error('No gauge ID provided'),
          loading: false,
        }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, loading: true }));

        const response = await fetch(
          `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=${stream.gauge.id}&parameterCd=00065`,
          {
            signal: controller.signal,
            headers: { Accept: 'application/json' },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const latestValue = data.value.timeSeries[0].values[0].value[0];

        const newReading: GaugeReading = {
          value: parseFloat(latestValue.value),
          timestamp: latestValue.dateTime,
        };

        if (!mounted) return;

        // Update previous reading before setting new one
        setPreviousReading(state.reading);

        // Calculate new state
        const status = determineLevel(newReading.value, stream.targetLevels);
        const trend = determineTrend(newReading, previousReading);

        setState({
          currentLevel: { status, trend },
          reading: newReading,
          loading: false,
          error: null,
        });
      } catch (err) {
        if (!mounted) return;
        setState((prev) => ({
          ...prev,
          error:
            err instanceof Error
              ? err
              : new Error('Failed to fetch gauge data'),
          loading: false,
        }));
      }
    };

    fetchGaugeData();
    const interval = setInterval(fetchGaugeData, 15 * 60 * 1000); // 15 minutes

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, [stream.gauge.id]);

  return state;
}
