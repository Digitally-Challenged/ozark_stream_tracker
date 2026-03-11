const NWS_BASE = 'https://api.water.noaa.gov/nwps/v1/gauges';
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const FETCH_TIMEOUT_MS = 5000;

export interface NwsForecastPoint {
  validTime: string;
  stage: number;
  flow: number;
}

export interface NwsFloodCategories {
  action: number;
  minor: number;
  moderate: number;
  major: number;
}

export interface NwsForecast {
  gaugeId: string;
  data: NwsForecastPoint[];
  peakForecast: { stage: number; time: string } | null;
  floodCategories: NwsFloodCategories | null;
}

interface CacheEntry {
  data: NwsForecast;
  timestamp: number;
}

function getCached(gaugeId: string): NwsForecast | null {
  try {
    const raw = localStorage.getItem(`nws-forecast-${gaugeId}`);
    if (!raw) return null;
    const entry: CacheEntry = JSON.parse(raw);
    if (Date.now() - entry.timestamp > CACHE_TTL_MS) return null;
    return entry.data;
  } catch {
    return null;
  }
}

function setCache(gaugeId: string, data: NwsForecast): void {
  try {
    const entry: CacheEntry = { data, timestamp: Date.now() };
    localStorage.setItem(`nws-forecast-${gaugeId}`, JSON.stringify(entry));
  } catch {
    // localStorage full — ignore
  }
}

export async function fetchNwsForecast(
  gaugeId: string
): Promise<NwsForecast | null> {
  const cached = getCached(gaugeId);
  if (cached) return cached;

  try {
    const stageRes = await fetch(`${NWS_BASE}/${gaugeId}/stageflow`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    if (!stageRes.ok) return null;

    const stageData = await stageRes.json();
    const points: NwsForecastPoint[] = (stageData.data ?? []).map(
      (d: { validTime: string; primary: number; secondary: number }) => ({
        validTime: d.validTime,
        stage: d.primary,
        flow: d.secondary,
      })
    );

    // Find peak forecast
    let peakForecast: { stage: number; time: string } | null = null;
    for (const p of points) {
      if (!peakForecast || p.stage > peakForecast.stage) {
        peakForecast = { stage: p.stage, time: p.validTime };
      }
    }

    // Fetch flood categories
    let floodCategories: NwsFloodCategories | null = null;
    try {
      const gaugeRes = await fetch(`${NWS_BASE}/${gaugeId}`, {
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      });
      if (gaugeRes.ok) {
        const gaugeInfo = await gaugeRes.json();
        const cats = gaugeInfo.flood?.categories;
        if (Array.isArray(cats) && cats.length > 0) {
          const catMap: Record<string, number> = {};
          for (const c of cats) {
            catMap[c.category] = c.stage;
          }
          if (catMap.action) {
            floodCategories = {
              action: catMap.action,
              minor: catMap.minor ?? 0,
              moderate: catMap.moderate ?? 0,
              major: catMap.major ?? 0,
            };
          }
        }
      }
    } catch {
      // Flood categories are optional — ignore errors
    }

    const forecast: NwsForecast = {
      gaugeId,
      data: points,
      peakForecast,
      floodCategories,
    };

    setCache(gaugeId, forecast);
    return forecast;
  } catch {
    return null;
  }
}
