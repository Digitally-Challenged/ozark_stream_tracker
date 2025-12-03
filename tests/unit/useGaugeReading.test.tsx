import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useGaugeReading } from '../../src/hooks/useGaugeReading';
import { LevelTrend, LevelStatus } from '../../src/types/stream';

// Mock the GaugeDataContext
const mockGauges = new Map();

vi.mock('../../src/context/GaugeDataContext', () => ({
  useGaugeDataContext: () => ({
    gauges: mockGauges,
    isLoading: false,
  }),
}));

describe('useGaugeReading', () => {
  const targetLevels = {
    tooLow: 3.0,
    optimal: 5.0,
    high: 7.0,
  };

  beforeEach(() => {
    mockGauges.clear();
  });

  it('should return trend when previousReading is provided', () => {
    // Set up mock gauge data with both current and previous readings
    mockGauges.set('07196500', {
      reading: {
        value: 5.5,
        timestamp: '2025-12-03T12:30:00.000Z',
        dateTime: '2025-12-03T12:30:00.000Z',
      },
      previousReading: {
        value: 5.3, // 0.2 higher = Rising
        timestamp: '2025-12-03T10:00:00.000Z',
        dateTime: '2025-12-03T10:00:00.000Z',
      },
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel?.trend).toBe(LevelTrend.Rising);
  });

  it('should return Falling trend when water level drops', () => {
    mockGauges.set('07196500', {
      reading: {
        value: 5.0,
        timestamp: '2025-12-03T12:30:00.000Z',
        dateTime: '2025-12-03T12:30:00.000Z',
      },
      previousReading: {
        value: 5.3,
        timestamp: '2025-12-03T10:00:00.000Z',
        dateTime: '2025-12-03T10:00:00.000Z',
      },
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel?.trend).toBe(LevelTrend.Falling);
  });

  it('should return Holding trend when water level is stable', () => {
    mockGauges.set('07196500', {
      reading: {
        value: 5.05,
        timestamp: '2025-12-03T12:30:00.000Z',
        dateTime: '2025-12-03T12:30:00.000Z',
      },
      previousReading: {
        value: 5.0, // 0.05 difference < 0.1 threshold
        timestamp: '2025-12-03T10:00:00.000Z',
        dateTime: '2025-12-03T10:00:00.000Z',
      },
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel?.trend).toBe(LevelTrend.Holding);
  });

  it('should return None trend when no previousReading exists', () => {
    mockGauges.set('07196500', {
      reading: {
        value: 5.0,
        timestamp: '2025-12-03T12:30:00.000Z',
        dateTime: '2025-12-03T12:30:00.000Z',
      },
      previousReading: null, // No previous reading!
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel?.trend).toBe(LevelTrend.None);
  });

  it('should return correct level status', () => {
    mockGauges.set('07196500', {
      reading: {
        value: 5.5, // Between optimal (5.0) and high (7.0)
        timestamp: '2025-12-03T12:30:00.000Z',
        dateTime: '2025-12-03T12:30:00.000Z',
      },
      previousReading: null,
      loading: false,
      error: null,
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel?.status).toBe(LevelStatus.Optimal);
  });

  it('should return undefined currentLevel when no gauge data', () => {
    // Don't add any gauge data to mockGauges

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel).toBeUndefined();
    expect(result.current.reading).toBeNull();
  });

  it('should return undefined currentLevel when reading is null', () => {
    mockGauges.set('07196500', {
      reading: null,
      previousReading: null,
      loading: false,
      error: new Error('No data available'),
    });

    const { result } = renderHook(() =>
      useGaugeReading('07196500', targetLevels)
    );

    expect(result.current.currentLevel).toBeUndefined();
    expect(result.current.error).toBeInstanceOf(Error);
  });
});
