import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchPrecipTotals } from '../../src/services/precipQueryService';

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

const MOCK_IDENTIFY_RESPONSE = {
  results: [
    {
      layerId: 28,
      layerName: 'Image',
      value: '',
      attributes: { 'Service Pixel Value': '1.23' },
    },
    {
      layerId: 36,
      layerName: 'Image',
      value: '',
      attributes: { 'Service Pixel Value': '2.85' },
    },
    {
      layerId: 40,
      layerName: 'Image',
      value: '',
      attributes: { 'Service Pixel Value': '3.12' },
    },
    {
      layerId: 56,
      layerName: 'Image',
      value: '',
      attributes: { 'Service Pixel Value': '4.50' },
    },
  ],
};

describe('fetchPrecipTotals', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorageMock.clear();
  });

  it('parses identify response into precipitation totals', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_IDENTIFY_RESPONSE),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.gaugeId).toBe('07252000');
    expect(result.last24h).toBeCloseTo(1.23);
    expect(result.last48h).toBeCloseTo(2.85);
    expect(result.last72h).toBeCloseTo(3.12);
    expect(result.last7d).toBeCloseTo(4.5);
  });

  it('returns null values for missing layers', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
    expect(result.last48h).toBeNull();
  });

  it('handles NoData pixel values', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          results: [
            {
              layerId: 28,
              layerName: 'Image',
              value: '',
              attributes: { 'Service Pixel Value': 'NoData' },
            },
          ],
        }),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
  });

  it('uses cached data within TTL', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        lat: 35.5,
        lng: -94.0,
        last24h: 1.0,
        last48h: 2.0,
        last72h: null,
        last7d: null,
      },
      timestamp: Date.now(),
    };
    localStorageMock.setItem('precip-07252000', JSON.stringify(cached));

    global.fetch = vi.fn();
    const result = await fetchPrecipTotals('07252000', 35.5, -94.0);
    expect(result.last24h).toBe(1.0);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('returns null values on fetch error', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'));

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
    expect(result.last48h).toBeNull();
  });
});
