import { StreamData, StreamGauge, LevelStatus } from '../types/stream';
import { STATUS_HEX_COLORS } from './streamLevels';

export interface Watershed {
  gauge: StreamGauge;
  streams: StreamData[];
}

const NEUTRAL_GRAY = '#9e9e9e';

/** Priority: High (safety concern) > Optimal (runnable) > Low > TooLow */
const STATUS_PRIORITY: Record<LevelStatus, number> = {
  [LevelStatus.High]: 4,
  [LevelStatus.Optimal]: 3,
  [LevelStatus.Low]: 2,
  [LevelStatus.TooLow]: 1,
};

/** Groups streams by their shared gauge ID into watershed buckets. */
export function groupStreamsByWatershed(
  streams: StreamData[]
): Map<string, Watershed> {
  const watersheds = new Map<string, Watershed>();

  for (const stream of streams) {
    const existing = watersheds.get(stream.gauge.id);
    if (existing) {
      existing.streams.push(stream);
    } else {
      watersheds.set(stream.gauge.id, {
        gauge: stream.gauge,
        streams: [stream],
      });
    }
  }

  return watersheds;
}

/** Returns the hex color for the highest-priority status in the array. */
export function getWatershedMarkerColor(statuses: LevelStatus[]): string {
  if (statuses.length === 0) return NEUTRAL_GRAY;

  let highestPriority = 0;
  let highestStatus: LevelStatus = LevelStatus.TooLow;

  for (const status of statuses) {
    const priority = STATUS_PRIORITY[status];
    if (priority > highestPriority) {
      highestPriority = priority;
      highestStatus = status;
    }
  }

  return STATUS_HEX_COLORS[highestStatus];
}
