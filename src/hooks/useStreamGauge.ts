import { useEffect, useMemo, useReducer } from 'react';
import { Stream, GaugeReading, LevelTrend } from '../types/stream';

// Constants
const USGS_API_BASE_URL = 'https://waterservices.usgs.gov/nwis/iv/';
const TREND_THRESHOLD = 0.1; // Minimum change to consider rising/falling (in feet)
const UPDATE_INTERVAL = 15 * 60 * 1000; // 15 minutes

// Types
interface USGSResponse {
  value: {
    timeSeries: [{
      values: [{
        value: Array<{
          value: string;
          dateTime: string;
        }>;
      }];
    }];
  };
}

type WaterLevel = 'X' | 'L' | 'O' | 'H';

interface GaugeState {
  reading: GaugeReading | null;
  previousReading: GaugeReading | null;
  loading: boolean;
  error: Error | null;
}

type GaugeAction = 
  | { type: 'SET_LOADING' }
  | { type: 'SET_ERROR'; payload: Error }
  | { type: 'SET_READING'; payload: GaugeReading }
  | { type: 'RESET_ERROR' };

const initialState: GaugeState = {
  reading: null,
  previousReading: null,
  loading: true,
  error: null
};

function gaugeReducer(state: GaugeState, action: GaugeAction): GaugeState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: true };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_READING':
      return {
        ...state,
        previousReading: state.reading,
        reading: action.payload,
        loading: false,
        error: null
      };
    case 'RESET_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
}

// Pure functions
const calculateStatus = (value: number, targetLevels: Stream['targetLevels']): WaterLevel => {
  if (value < targetLevels.tooLow) return 'X';
  if (value < targetLevels.optimal) return 'L';
  if (value < targetLevels.high) return 'O';
  return 'H';
};

const transformGaugeData = (data: USGSResponse): GaugeReading => {
  const latestReading = data.value.timeSeries[0].values[0].value[0];
  return {
    value: parseFloat(latestReading.value),
    timestamp: latestReading.dateTime
  };
};

const determineTrend = (current: GaugeReading | null, previous: GaugeReading | null): LevelTrend => {
  if (!current || !previous) return LevelTrend.None;
  
  const difference = current.value - previous.value;
  if (Math.abs(difference) < TREND_THRESHOLD) return LevelTrend.Holding;
  return difference > 0 ? LevelTrend.Rising : LevelTrend.Falling;
};

export function useStreamGauge(stream: Stream) {
  const [state, dispatch] = useReducer(gaugeReducer, initialState);
  
  useEffect(() => {
    let mounted = true;
    let retryCount = 0;
    const MAX_RETRIES = 3;
    
    const fetchGaugeData = async () => {
      if (!stream.gauge.id) {
        dispatch({ type: 'SET_ERROR', payload: new Error('No gauge ID provided') });
        return;
      }

      try {
        dispatch({ type: 'SET_LOADING' });
        const url = new URL(USGS_API_BASE_URL);
        url.searchParams.append('format', 'json');
        url.searchParams.append('sites', stream.gauge.id);
        url.searchParams.append('parameterCd', '00065');

        const response = await fetch(url.toString(), {
          headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: USGSResponse = await response.json();
        
        if (!mounted) return;

        if (!data.value?.timeSeries?.[0]?.values?.[0]?.value?.[0]) {
          throw new Error('Invalid gauge data format');
        }

        const newReading = transformGaugeData(data);
        dispatch({ type: 'SET_READING', payload: newReading });
        retryCount = 0;
      } catch (err) {
        if (!mounted) return;
        
        if (retryCount < MAX_RETRIES) {
          retryCount++;
          setTimeout(fetchGaugeData, 1000 * retryCount);
          return;
        }
        
        dispatch({ 
          type: 'SET_ERROR', 
          payload: err instanceof Error ? err : new Error('Failed to fetch gauge data')
        });
      }
    };

    fetchGaugeData();
    const interval = setInterval(fetchGaugeData, UPDATE_INTERVAL);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [stream.gauge.id]);

  const currentLevel = useMemo(() => {
    if (!state.reading) return undefined;
    
    return {
      status: calculateStatus(state.reading.value, stream.targetLevels),
      trend: determineTrend(state.reading, state.previousReading)
    };
  }, [state.reading, state.previousReading, stream.targetLevels]);

  return {
    currentLevel,
    reading: state.reading,
    loading: state.loading,
    error: state.error
  };
}