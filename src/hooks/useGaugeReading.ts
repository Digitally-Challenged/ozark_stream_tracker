// src/hooks/useGaugeReading.ts
import { useMemo, useEffect, useRef } from 'react';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { GaugeReading, LevelStatus, LevelTrend, TargetLevels } from '../types/stream';
import { determineLevel, determineTrend } from '../utils/streamLevels';
import { useGaugeHistory } from './useGaugeHistory';

interface UseGaugeReadingResult {
  reading: GaugeReading | null;
  currentLevel: {
    status: LevelStatus;
    trend: LevelTrend;
  } | undefined;
  loading: boolean;
  error: Error | null;
}

export function useGaugeReading(
  gaugeId: string,
  targetLevels: TargetLevels
): UseGaugeReadingResult {
  const { gauges, isLoading } = useGaugeDataContext();
  const { addReading, getPreviousReading } = useGaugeHistory(gaugeId);
  const lastReadingRef = useRef<string | null>(null);

  const gaugeData = gauges.get(gaugeId);

  const result = useMemo(() => {
    if (!gaugeData) {
      return {
        reading: null,
        currentLevel: undefined,
        loading: isLoading,
        error: null,
      };
    }

    const { reading, loading, error } = gaugeData;

    if (!reading) {
      return {
        reading: null,
        currentLevel: undefined,
        loading: loading || isLoading,
        error,
      };
    }

    // Calculate level status
    const status = determineLevel(reading.value, targetLevels);

    // Get previous reading for trend calculation
    const previousReading = getPreviousReading();
    const trend = previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;

    return {
      reading,
      currentLevel: { status, trend },
      loading: false,
      error: null,
    };
  }, [gaugeData, isLoading, targetLevels, getPreviousReading]);

  // Store reading in history AFTER render (side effect)
  useEffect(() => {
    if (result.reading && result.reading.timestamp !== lastReadingRef.current) {
      lastReadingRef.current = result.reading.timestamp ?? null;
      addReading(result.reading);
    }
  }, [result.reading, addReading]);

  return result;
}
