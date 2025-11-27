// src/hooks/useStreamStatus.ts
import { useMemo } from 'react';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { StreamData, LevelStatus } from '../types/stream';
import { determineLevel } from '../utils/streamLevels';

export function useStreamStatus(stream: StreamData): LevelStatus | undefined {
  const { gauges } = useGaugeDataContext();

  return useMemo(() => {
    const gaugeData = gauges.get(stream.gauge.id);
    if (!gaugeData?.reading) {
      return undefined;
    }
    return determineLevel(gaugeData.reading.value, stream.targetLevels);
  }, [gauges, stream.gauge.id, stream.targetLevels]);
}

export function useAllStreamStatuses(
  streams: StreamData[]
): Map<string, LevelStatus | undefined> {
  const { gauges } = useGaugeDataContext();

  return useMemo(() => {
    const statuses = new Map<string, LevelStatus | undefined>();

    streams.forEach(stream => {
      const gaugeData = gauges.get(stream.gauge.id);
      if (gaugeData?.reading) {
        statuses.set(stream.name, determineLevel(gaugeData.reading.value, stream.targetLevels));
      } else {
        statuses.set(stream.name, undefined);
      }
    });

    return statuses;
  }, [gauges, streams]);
}
