import { describe, it, expect } from 'vitest';
import { filterByRatingAndSize } from '../../src/utils/filterStreams';
import { StreamData } from '../../src/types/stream';

const mockStream = (name: string, rating: string, size: string): StreamData =>
  ({
    name,
    rating,
    size,
    gauge: { id: '1', name: 'test', url: '' },
    quality: 'A',
    targetLevels: { tooLow: 1, optimal: 2, high: 3 },
  }) as StreamData;

describe('filterByRatingAndSize', () => {
  const streams = [
    mockStream('Creek A', '5', 'S'),
    mockStream('Creek B', '3', 'M'),
    mockStream('Creek C', '5', 'L'),
  ];

  it('returns all streams when no filters applied', () => {
    expect(filterByRatingAndSize(streams, [], [])).toHaveLength(3);
  });

  it('filters by rating', () => {
    const result = filterByRatingAndSize(streams, ['5'], []);
    expect(result).toHaveLength(2);
    expect(result.map((s) => s.name)).toEqual(['Creek A', 'Creek C']);
  });

  it('filters by size', () => {
    const result = filterByRatingAndSize(streams, [], ['M']);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('Creek B');
  });

  it('filters by both rating and size', () => {
    const result = filterByRatingAndSize(streams, ['5'], ['S']);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('Creek A');
  });
});
