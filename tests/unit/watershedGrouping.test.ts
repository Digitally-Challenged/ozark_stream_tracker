import { describe, it, expect } from 'vitest';
import { LevelStatus } from '../../src/types/stream';
import {
  groupStreamsByWatershed,
  getWatershedMarkerColor,
} from '../../src/utils/watershedGrouping';

describe('groupStreamsByWatershed', () => {
  it('groups streams sharing the same gauge ID', () => {
    const streams = [
      {
        name: 'Stream A',
        rating: 'III',
        size: 'S' as const,
        gauge: { name: 'Gauge 1', id: '001', url: '' },
        quality: 'A' as const,
        targetLevels: { tooLow: 1, optimal: 2, high: 3 },
      },
      {
        name: 'Stream B',
        rating: 'II',
        size: 'M' as const,
        gauge: { name: 'Gauge 1', id: '001', url: '' },
        quality: 'B' as const,
        targetLevels: { tooLow: 2, optimal: 3, high: 4 },
      },
      {
        name: 'Stream C',
        rating: 'IV',
        size: 'L' as const,
        gauge: { name: 'Gauge 2', id: '002', url: '' },
        quality: 'A' as const,
        targetLevels: { tooLow: 1, optimal: 2, high: 3 },
      },
    ];

    const result = groupStreamsByWatershed(streams);
    expect(result.size).toBe(2);
    expect(result.get('001')!.streams).toHaveLength(2);
    expect(result.get('002')!.streams).toHaveLength(1);
    expect(result.get('001')!.gauge.name).toBe('Gauge 1');
  });
});

describe('getWatershedMarkerColor', () => {
  it('returns High color when any stream is High', () => {
    const statuses = [LevelStatus.Optimal, LevelStatus.High, LevelStatus.Low];
    expect(getWatershedMarkerColor(statuses)).toBe('#0288d1');
  });

  it('returns Optimal color when best is Optimal (no High)', () => {
    const statuses = [LevelStatus.Optimal, LevelStatus.Low, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#2e7d32');
  });

  it('returns Low color when best is Low', () => {
    const statuses = [LevelStatus.Low, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#ed6c02');
  });

  it('returns TooLow color when all Too Low', () => {
    const statuses = [LevelStatus.TooLow, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#d32f2f');
  });

  it('returns neutral gray for empty array', () => {
    expect(getWatershedMarkerColor([])).toBe('#9e9e9e');
  });
});
