import { describe, it, expect } from 'vitest';
import { LevelTrend } from '../../src/types/stream';
import { getTrendLabel, getTrendMuiColor } from '../../src/utils/trendUtils';

describe('getTrendLabel', () => {
  it('returns Rising for rising trend', () => {
    expect(getTrendLabel(LevelTrend.Rising)).toBe('Rising');
  });

  it('returns Falling for falling trend', () => {
    expect(getTrendLabel(LevelTrend.Falling)).toBe('Falling');
  });

  it('returns Stable for holding trend', () => {
    expect(getTrendLabel(LevelTrend.Holding)).toBe('Stable');
  });

  it('returns null for none trend', () => {
    expect(getTrendLabel(LevelTrend.None)).toBeNull();
  });
});

describe('getTrendMuiColor', () => {
  it('returns success.main for rising', () => {
    expect(getTrendMuiColor(LevelTrend.Rising)).toBe('success.main');
  });

  it('returns error.main for falling', () => {
    expect(getTrendMuiColor(LevelTrend.Falling)).toBe('error.main');
  });

  it('returns warning.main for holding', () => {
    expect(getTrendMuiColor(LevelTrend.Holding)).toBe('warning.main');
  });

  it('returns null for none', () => {
    expect(getTrendMuiColor(LevelTrend.None)).toBeNull();
  });
});
