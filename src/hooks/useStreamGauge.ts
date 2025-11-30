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
import { useGaugeHistory } from './useGaugeHistory';

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

  const { addReading, getPreviousReading } = useGaugeHistory(stream.gauge.id);

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
          // Regular USGS gauge - get current reading only
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

          if (
            !data.value ||
            !data.value.timeSeries ||
            data.value.timeSeries.length === 0
          ) {
            throw new Error('No data available from USGS');
          }

          const latestValue = data.value.timeSeries[0].values[0].value[0];

          newReading = {
            value: parseFloat(latestValue.value),
            timestamp: latestValue.dateTime,
            dateTime: latestValue.dateTime,
          };
        }

        if (!mounted) return;

        // Get previous reading from storage BEFORE adding new one
        const previousReading = getPreviousReading();

        // Add current reading to history for next comparison
        addReading(newReading);

        // Calculate new state
        const status = determineLevel(newReading.value, stream.targetLevels);

        // Simple trend calculation: current vs previous
        const trend = previousReading
          ? determineTrend(newReading, previousReading)
          : LevelTrend.None;

        // Log real trend calculation
        if (previousReading) {
          const change = newReading.value - previousReading.value;
          console.log(
            `[${stream.name}] TREND: ${trend} | Previous: ${previousReading.value}ft → Current: ${newReading.value}ft | Change: ${change > 0 ? '+' : ''}${change.toFixed(3)}ft`
          );
        } else {
          console.log(
            `[${stream.name}] No previous reading - trend will appear on next update`
          );
        }

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
    const interval = setInterval(
      fetchGaugeData,
      API_CONFIG.REFRESH_INTERVAL_MS
    );

    return () => {
      mounted = false;
      controller.abort();
      clearInterval(interval);
    };
  }, [stream.gauge.id, stream.targetLevels]);

  return state;
}
