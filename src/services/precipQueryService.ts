const QPE_BASE =
  'https://mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer/identify';
const CACHE_TTL_MS = 30 * 60 * 1000; // 30 minutes
const FETCH_TIMEOUT_MS = 5000;

// Layer IDs for precipitation periods
const LAYER_IDS = {
  last24h: 17,
  last48h: 23,
  last72h: 29,
  last7d: 35,
} as const;

export interface PrecipTotals {
  gaugeId: string;
  lat: number;
  lng: number;
  last24h: number | null;
  last48h: number | null;
  last72h: number | null;
  last7d: number | null;
}

interface CacheEntry {
  data: PrecipTotals;
  timestamp: number;
}

function getCached(gaugeId: string): PrecipTotals | null {
  try {
    const raw = localStorage.getItem(`precip-${gaugeId}`);
    if (!raw) return null;
    const entry: CacheEntry = JSON.parse(raw);
    if (Date.now() - entry.timestamp > CACHE_TTL_MS) return null;
    return entry.data;
  } catch {
    return null;
  }
}

function setCache(gaugeId: string, data: PrecipTotals): void {
  try {
    const entry: CacheEntry = { data, timestamp: Date.now() };
    localStorage.setItem(`precip-${gaugeId}`, JSON.stringify(entry));
  } catch {
    // localStorage full — ignore
  }
}

function parsePixelValue(value: string): number | null {
  if (!value || value === 'NoData' || value === 'Null') return null;
  const match = value.match(/Pixel Value:\s*([\d.]+)/);
  if (!match) return null;
  const num = parseFloat(match[1]);
  return isNaN(num) ? null : num;
}

export async function fetchPrecipTotals(
  gaugeId: string,
  lat: number,
  lng: number
): Promise<PrecipTotals> {
  const empty: PrecipTotals = {
    gaugeId,
    lat,
    lng,
    last24h: null,
    last48h: null,
    last72h: null,
    last7d: null,
  };

  const cached = getCached(gaugeId);
  if (cached) return cached;

  try {
    const layerList = Object.values(LAYER_IDS).join(',');
    const geometry = JSON.stringify({
      x: lng,
      y: lat,
      spatialReference: { wkid: 4326 },
    });
    const extent = `${lng - 0.5},${lat - 0.5},${lng + 0.5},${lat + 0.5}`;

    const params = new URLSearchParams({
      geometry,
      geometryType: 'esriGeometryPoint',
      layers: `visible:${layerList}`,
      mapExtent: extent,
      imageDisplay: '600,550,96',
      returnGeometry: 'false',
      f: 'json',
    });

    const res = await fetch(`${QPE_BASE}?${params}`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });

    if (!res.ok) return empty;

    const data = await res.json();
    const results: Array<{ layerId: number; value: string }> =
      data.results ?? [];

    const byLayer = new Map<number, string>();
    for (const r of results) {
      byLayer.set(r.layerId, r.value);
    }

    const totals: PrecipTotals = {
      gaugeId,
      lat,
      lng,
      last24h: parsePixelValue(byLayer.get(LAYER_IDS.last24h) ?? ''),
      last48h: parsePixelValue(byLayer.get(LAYER_IDS.last48h) ?? ''),
      last72h: parsePixelValue(byLayer.get(LAYER_IDS.last72h) ?? ''),
      last7d: parsePixelValue(byLayer.get(LAYER_IDS.last7d) ?? ''),
    };

    setCache(gaugeId, totals);
    return totals;
  } catch {
    return empty;
  }
}
