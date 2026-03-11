import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchNwsForecast } from '../../src/services/nwsForecastService';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(global, 'localStorage', { value: localStorageMock });

const MOCK_STAGEFLOW = {
  primaryName: 'Stage',
  primaryUnits: 'ft',
  secondaryName: 'Flow',
  secondaryUnits: 'kcfs',
  data: [
    { validTime: '2026-03-10T12:00:00Z', primary: 3.5, secondary: 1.2 },
    { validTime: '2026-03-10T18:00:00Z', primary: 3.8, secondary: 1.4 },
    { validTime: '2026-03-11T00:00:00Z', primary: 4.2, secondary: 1.7 },
    { validTime: '2026-03-11T12:00:00Z', primary: 5.1, secondary: 2.3 },
    { validTime: '2026-03-12T00:00:00Z', primary: 4.8, secondary: 2.1 },
  ],
};

const MOCK_GAUGE_INFO = {
  flood: {
    categories: [
      { category: 'action', stage: 10 },
      { category: 'minor', stage: 18 },
      { category: 'moderate', stage: 20 },
      { category: 'major', stage: 22 },
    ],
  },
};

describe('fetchNwsForecast', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorageMock.clear();
  });

  it('parses stageflow response into forecast structure', async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_STAGEFLOW),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_GAUGE_INFO),
      });

    const result = await fetchNwsForecast('07252000');
    expect(result).not.toBeNull();
    expect(result!.gaugeId).toBe('07252000');
    expect(result!.data.length).toBe(5);
    expect(result!.data[0].stage).toBe(3.5);
    expect(result!.peakForecast!.stage).toBe(5.1);
    expect(result!.floodCategories).not.toBeNull();
    expect(result!.floodCategories!.action).toBe(10);
  });

  it('returns null when stageflow returns 404', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({ ok: false, status: 404 });

    const result = await fetchNwsForecast('99999999');
    expect(result).toBeNull();
  });

  it('uses cached data within TTL', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        data: [],
        peakForecast: null,
        floodCategories: null,
      },
      timestamp: Date.now(),
    };
    localStorageMock.setItem('nws-forecast-07252000', JSON.stringify(cached));

    global.fetch = vi.fn();
    const result = await fetchNwsForecast('07252000');
    expect(result).toEqual(cached.data);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('refetches when cache is expired', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        data: [],
        peakForecast: null,
        floodCategories: null,
      },
      timestamp: Date.now() - 2 * 60 * 60 * 1000, // 2 hours ago
    };
    localStorageMock.setItem('nws-forecast-07252000', JSON.stringify(cached));

    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_STAGEFLOW),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_GAUGE_INFO),
      });

    const result = await fetchNwsForecast('07252000');
    expect(global.fetch).toHaveBeenCalled();
    expect(result!.data.length).toBe(5);
  });
});
