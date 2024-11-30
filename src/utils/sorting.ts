import { StreamData, LevelTrend } from '../types/stream';
import { SortDirection, SortField } from '../types/table';

// Helper function to get trend priority (Rising > Holding > Falling > None)
const getTrendPriority = (trend: LevelTrend | undefined): number => {
  switch (trend) {
    case LevelTrend.Rising: return 3;
    case LevelTrend.Holding: return 2;
    case LevelTrend.Falling: return 1;
    default: return 0;
  }
};

export function sortStreams(
  streams: StreamData[], 
  sortField: SortField, 
  sortDirection: SortDirection
): StreamData[] {
  return [...streams].sort((a, b) => {
    let comparison = 0;
    let trendA: number, trendB: number;

    switch (sortField) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'rating':
        comparison = a.rating.localeCompare(b.rating);
        break;
      case 'size':
        comparison = a.size.localeCompare(b.size);
        break;
      case 'gauge':
        comparison = a.gauge.name.localeCompare(b.gauge.name);
        break;
      case 'quality':
        comparison = a.quality.localeCompare(b.quality);
        break;
      case 'trend':
        trendA = getTrendPriority(a.currentLevel?.trend);
        trendB = getTrendPriority(b.currentLevel?.trend);
        comparison = trendB - trendA; // Higher priority first
        break;
      case 'level':
        if (a.currentLevel?.status && b.currentLevel?.status) {
          comparison = a.currentLevel.status.localeCompare(b.currentLevel.status);
        }
        break;
      case 'reading':
        const readingA = a.currentFlow ?? -Infinity;
        const readingB = b.currentFlow ?? -Infinity;
        comparison = readingA - readingB;
        break;
      default:
        comparison = 0;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });
}