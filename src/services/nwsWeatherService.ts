const FORECAST_CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const FETCH_TIMEOUT_MS = 5000;

export interface WeatherPeriod {
  name: string;
  temperature: number;
  precipChance: number;
  shortForecast: string;
  isDaytime: boolean;
  startTime: string;
}

export interface WeatherForecastData {
  periods: WeatherPeriod[];
  fetchedAt: number;
}

interface ForecastCacheEntry {
  data: WeatherForecastData;
  timestamp: number;
}

function getCachedForecast(key: string): WeatherForecastData | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const entry: ForecastCacheEntry = JSON.parse(raw);
    if (Date.now() - entry.timestamp > FORECAST_CACHE_TTL_MS) return null;
    return entry.data;
  } catch {
    return null;
  }
}

function setCachedForecast(key: string, data: WeatherForecastData): void {
  try {
    const entry: ForecastCacheEntry = { data, timestamp: Date.now() };
    localStorage.setItem(key, JSON.stringify(entry));
  } catch {
    // localStorage full — ignore
  }
}

function getCachedGridUrl(lat: number, lng: number): string | null {
  try {
    const raw = localStorage.getItem(`nws-grid-${lat},${lng}`);
    return raw;
  } catch {
    return null;
  }
}

function setCachedGridUrl(lat: number, lng: number, url: string): void {
  try {
    localStorage.setItem(`nws-grid-${lat},${lng}`, url);
  } catch {
    // ignore
  }
}

async function getForecastUrl(
  lat: number,
  lng: number
): Promise<string | null> {
  const cached = getCachedGridUrl(lat, lng);
  if (cached) return cached;

  try {
    const res = await fetch(
      `https://api.weather.gov/points/${lat.toFixed(4)},${lng.toFixed(4)}`,
      {
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
        headers: { Accept: 'application/geo+json' },
      }
    );
    if (!res.ok) return null;
    const data = await res.json();
    const url = data.properties?.forecast;
    if (url) setCachedGridUrl(lat, lng, url);
    return url ?? null;
  } catch {
    return null;
  }
}

export async function fetchWeatherForecast(
  lat: number,
  lng: number
): Promise<WeatherForecastData | null> {
  const cacheKey = `nws-weather-${lat.toFixed(4)},${lng.toFixed(4)}`;
  const cached = getCachedForecast(cacheKey);
  if (cached) return cached;

  const forecastUrl = await getForecastUrl(lat, lng);
  if (!forecastUrl) return null;

  try {
    const res = await fetch(forecastUrl, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      headers: { 'User-Agent': 'OzarkCreekFlowZone/1.0' },
    });
    if (!res.ok) return null;
    const data = await res.json();

    const rawPeriods = data.properties?.periods ?? [];
    const periods: WeatherPeriod[] = rawPeriods
      .filter((p: { isDaytime: boolean }) => p.isDaytime)
      .slice(0, 5)
      .map(
        (p: {
          name: string;
          temperature: number;
          probabilityOfPrecipitation: { value: number | null };
          shortForecast: string;
          isDaytime: boolean;
          startTime: string;
        }) => ({
          name: p.name,
          temperature: p.temperature,
          precipChance: p.probabilityOfPrecipitation?.value ?? 0,
          shortForecast: p.shortForecast,
          isDaytime: p.isDaytime,
          startTime: p.startTime,
        })
      );

    const result: WeatherForecastData = {
      periods,
      fetchedAt: Date.now(),
    };

    setCachedForecast(cacheKey, result);
    return result;
  } catch {
    return null;
  }
}
