// src/hooks/useStreamGauge.ts
import { useState, useEffect } from 'react';
import {
  StreamData,
  GaugeReading,
  LevelStatus,
  LevelTrend,
} from '../types/stream';
import { determineLevel, determineTrend } from '../utils/streamLevels';
import { API_CONFIG } from '../constants';
import { TurnerBendScraper } from '../services/turnerBendScraper';

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

        let newReading: GaugeReading | null = null;

        // Check if this is the Turner Bend gauge
        if (stream.gauge.id === 'TURNER_BEND') {
          newReading = await TurnerBendScraper.fetchGaugeData();
          if (!newReading) {
            throw new Error('Failed to fetch Turner Bend data');
          }
        } else {
          // Regular USGS gauge
          const response = await fetch(
            `${API_CONFIG.USGS_BASE_URL}?format=json&sites=${stream.gauge.id}&parameterCd=${API_CONFIG.GAUGE_HEIGHT_PARAMETER}`,
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

          newReading = {
            value: parseFloat(latestValue.value),
            timestamp: latestValue.dateTime,
            dateTime: latestValue.dateTime,
          };
        }

        if (!mounted) return;

        // Update previous reading before setting new one
        setPreviousReading(state.reading);

        // Calculate new state
        const status = determineLevel(newReading.value, stream.targetLevels);
        const trend = previousReading ? determineTrend(newReading, previousReading) : LevelTrend.None;

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
    const interval = setInterval(fetchGaugeData, API_CONFIG.REFRESH_INTERVAL_MS);

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, [stream.gauge.id]);

  return state;
}
