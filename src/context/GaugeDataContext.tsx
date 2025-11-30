// src/context/GaugeDataContext.tsx
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { GaugeReading } from '../types/stream';
import { API_CONFIG } from '../constants';
import { streams } from '../data/streamData';
import { TurnerBendScraper } from '../services/turnerBendScraper';

interface GaugeData {
  reading: GaugeReading | null;
  loading: boolean;
  error: Error | null;
}

interface GaugeDataContextValue {
  gauges: Map<string, GaugeData>;
  lastUpdated: Date | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

const GaugeDataContext = createContext<GaugeDataContextValue | null>(null);

// Extract unique gauge IDs from stream data
function getUniqueGaugeIds(): string[] {
  const ids = new Set<string>();
  streams.forEach((stream) => {
    if (stream.gauge.id && stream.gauge.id !== 'TURNER_BEND') {
      ids.add(stream.gauge.id);
    }
  });
  return Array.from(ids);
}

interface GaugeDataProviderProps {
  children: ReactNode;
}

export function GaugeDataProvider({ children }: GaugeDataProviderProps) {
  const [gauges, setGauges] = useState<Map<string, GaugeData>>(new Map());
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAllGauges = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const newGauges = new Map<string, GaugeData>();
    const gaugeIds = getUniqueGaugeIds();

    try {
      // Batch fetch USGS gauges
      const response = await fetch(
        `${API_CONFIG.USGS_BASE_URL}?format=json&sites=${gaugeIds.join(',')}&parameterCd=${API_CONFIG.GAUGE_HEIGHT_PARAMETER}`,
        {
          headers: { Accept: 'application/json' },
          signal: AbortSignal.timeout(API_CONFIG.REQUEST_TIMEOUT_MS),
        }
      );

      if (!response.ok) {
        throw new Error(`USGS API error: ${response.status}`);
      }

      const data = await response.json();

      // Process each time series
      if (data.value?.timeSeries) {
        data.value.timeSeries.forEach((series: unknown) => {
          const typedSeries = series as {
            sourceInfo?: { siteCode?: Array<{ value?: string }> };
            values?: Array<{
              value?: Array<{ value?: string; dateTime?: string }>;
            }>;
          };
          const siteCode = typedSeries.sourceInfo?.siteCode?.[0]?.value;
          if (siteCode && typedSeries.values?.[0]?.value?.[0]) {
            const latestValue = typedSeries.values[0].value[0];
            newGauges.set(siteCode, {
              reading: {
                value: parseFloat(latestValue.value || '0'),
                timestamp: latestValue.dateTime,
                dateTime: latestValue.dateTime,
              },
              loading: false,
              error: null,
            });
          }
        });
      }

      // Mark missing gauges as unavailable
      gaugeIds.forEach((id) => {
        if (!newGauges.has(id)) {
          newGauges.set(id, {
            reading: null,
            loading: false,
            error: new Error('No data available'),
          });
        }
      });
    } catch (err) {
      setError(
        err instanceof Error ? err : new Error('Failed to fetch gauge data')
      );
      // Mark all as errored
      gaugeIds.forEach((id) => {
        newGauges.set(id, {
          reading: null,
          loading: false,
          error: err instanceof Error ? err : new Error('Failed to fetch'),
        });
      });
    }

    // Fetch Turner Bend separately
    try {
      const turnerBendReading = await TurnerBendScraper.fetchGaugeData();
      newGauges.set('TURNER_BEND', {
        reading: turnerBendReading,
        loading: false,
        error: turnerBendReading ? null : new Error('Turner Bend unavailable'),
      });
    } catch (err) {
      newGauges.set('TURNER_BEND', {
        reading: null,
        loading: false,
        error:
          err instanceof Error ? err : new Error('Turner Bend fetch failed'),
      });
    }

    setGauges(newGauges);
    setLastUpdated(new Date());
    setIsLoading(false);
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchAllGauges();
  }, [fetchAllGauges]);

  // Auto-refresh interval
  useEffect(() => {
    const interval = setInterval(
      fetchAllGauges,
      API_CONFIG.REFRESH_INTERVAL_MS
    );
    return () => clearInterval(interval);
  }, [fetchAllGauges]);

  return (
    <GaugeDataContext.Provider
      value={{
        gauges,
        lastUpdated,
        isLoading,
        error,
        refresh: fetchAllGauges,
      }}
    >
      {children}
    </GaugeDataContext.Provider>
  );
}

export function useGaugeDataContext() {
  const context = useContext(GaugeDataContext);
  if (!context) {
    throw new Error(
      'useGaugeDataContext must be used within GaugeDataProvider'
    );
  }
  return context;
}
