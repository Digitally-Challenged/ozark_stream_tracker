import { useState, useEffect } from 'react';
import { fetchNwsForecast, NwsForecast } from '../services/nwsForecastService';
import {
  fetchPrecipTotals,
  PrecipTotals,
} from '../services/precipQueryService';

export interface WatershedIntelligence {
  forecast: NwsForecast | null;
  precip: PrecipTotals | null;
  loading: boolean;
}

export function useWatershedIntelligence(
  gaugeId: string | null,
  lat: number | null,
  lng: number | null
): WatershedIntelligence {
  const [forecast, setForecast] = useState<NwsForecast | null>(null);
  const [precip, setPrecip] = useState<PrecipTotals | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!gaugeId || lat === null || lng === null) return;

    let cancelled = false;
    setLoading(true);

    Promise.all([
      fetchNwsForecast(gaugeId),
      fetchPrecipTotals(gaugeId, lat, lng),
    ]).then(([forecastResult, precipResult]) => {
      if (cancelled) return;
      setForecast(forecastResult);
      setPrecip(precipResult);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [gaugeId, lat, lng]);

  return { forecast, precip, loading };
}
