import { describe, it, expect } from 'vitest';
import { determineTrend } from '../../src/utils/streamLevels';
import { LevelTrend, GaugeReading } from '../../src/types/stream';
import { STREAM_LEVELS } from '../../src/constants';

describe('determineTrend', () => {
  const createReading = (value: number, timestamp?: string): GaugeReading => ({
    value,
    timestamp: timestamp || new Date().toISOString(),
    dateTime: timestamp || new Date().toISOString(),
  });

  it('should return Rising when current value is significantly higher than previous', () => {
    const current = createReading(5.5);
    const previous = createReading(5.3); // difference of 0.2 > threshold of 0.1

    const trend = determineTrend(current, previous);

    expect(trend).toBe(LevelTrend.Rising);
  });

  it('should return Falling when current value is significantly lower than previous', () => {
    const current = createReading(5.0);
    const previous = createReading(5.2); // difference of -0.2 > threshold

    const trend = determineTrend(current, previous);

    expect(trend).toBe(LevelTrend.Falling);
  });

  it('should return Holding when change is below threshold', () => {
    const current = createReading(5.05);
    const previous = createReading(5.0); // difference of 0.05 < threshold of 0.1

    const trend = determineTrend(current, previous);

    expect(trend).toBe(LevelTrend.Holding);
  });

  it('should return None when no previous reading is provided', () => {
    const current = createReading(5.0);

    const trend = determineTrend(current, undefined);

    expect(trend).toBe(LevelTrend.None);
  });

  it('should use the configured threshold from constants', () => {
    const threshold = STREAM_LEVELS.CHANGE_THRESHOLD;

    // At threshold - should still be Holding (uses < not <=)
    const current1 = createReading(5.0 + threshold);
    const previous1 = createReading(5.0);
    expect(determineTrend(current1, previous1)).toBe(LevelTrend.Holding);

    // Just above threshold - should be Rising
    const current2 = createReading(5.0 + threshold + 0.01);
    const previous2 = createReading(5.0);
    expect(determineTrend(current2, previous2)).toBe(LevelTrend.Rising);
  });

  it('should handle negative changes correctly', () => {
    const current = createReading(4.8);
    const previous = createReading(5.0); // -0.2

    const trend = determineTrend(current, previous);

    expect(trend).toBe(LevelTrend.Falling);
  });

  it('should handle exact same values as Holding', () => {
    const current = createReading(5.0);
    const previous = createReading(5.0);

    const trend = determineTrend(current, previous);

    expect(trend).toBe(LevelTrend.Holding);
  });
});
