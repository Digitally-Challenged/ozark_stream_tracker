// src/utils/streamGrouping.ts
import { StreamData, LevelStatus } from '../types/stream';

export interface GroupedStreams {
  [LevelStatus.Optimal]: StreamData[];
  [LevelStatus.Low]: StreamData[];
  [LevelStatus.High]: StreamData[];
  [LevelStatus.TooLow]: StreamData[];
}

export function groupStreamsByStatus(
  streams: StreamData[],
  getStatus: (stream: StreamData) => LevelStatus | undefined
): GroupedStreams {
  const groups: GroupedStreams = {
    [LevelStatus.Optimal]: [],
    [LevelStatus.Low]: [],
    [LevelStatus.High]: [],
    [LevelStatus.TooLow]: [],
  };

  streams.forEach((stream) => {
    const status = getStatus(stream);
    if (status && groups[status]) {
      groups[status].push(stream);
    } else {
      // Default to TooLow if no reading available
      groups[LevelStatus.TooLow].push(stream);
    }
  });

  return groups;
}

// Order for display (most useful first)
export const GROUP_ORDER: LevelStatus[] = [
  LevelStatus.Optimal,
  LevelStatus.Low,
  LevelStatus.High,
  LevelStatus.TooLow,
];
