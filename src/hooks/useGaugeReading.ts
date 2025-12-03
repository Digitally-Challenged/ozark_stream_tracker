// src/hooks/useGaugeReading.ts
import { useMemo } from 'react';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import {
  GaugeReading,
  LevelStatus,
  LevelTrend,
  TargetLevels,
} from '../types/stream';
import { determineLevel, determineTrend } from '../utils/streamLevels';

interface UseGaugeReadingResult {
  reading: GaugeReading | null;
  currentLevel:
    | {
        status: LevelStatus;
        trend: LevelTrend;
      }
    | undefined;
  loading: boolean;
  error: Error | null;
}

export function useGaugeReading(
  gaugeId: string,
  targetLevels: TargetLevels
): UseGaugeReadingResult {
  const { gauges, isLoading } = useGaugeDataContext();

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

    const { reading, previousReading, loading, error } = gaugeData;

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

    // Calculate trend from API-provided previous reading
    const trend = previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;

    return {
      reading,
      currentLevel: { status, trend },
      loading: false,
      error: null,
    };
  }, [gaugeData, isLoading, targetLevels]);

  return result;
}
