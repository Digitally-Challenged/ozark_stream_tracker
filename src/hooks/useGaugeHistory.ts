import { useState, useEffect, useCallback } from 'react';
import { GaugeReading } from '../types/stream';

interface GaugeHistoryEntry {
  gaugeId: string;
  reading: GaugeReading;
  timestamp: number;
}

/**
 * Hook to manage gauge reading history for trend calculation
 * Stores recent readings in localStorage to persist across sessions
 */
export function useGaugeHistory(gaugeId: string) {
  const STORAGE_KEY = 'gauge-reading-history';
  const MAX_HISTORY_HOURS = 24; // Keep 24 hours of history
  const MIN_TREND_INTERVAL_MINUTES = 30; // Minimum time between readings for trend calculation

  const [history, setHistory] = useState<GaugeHistoryEntry[]>([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: GaugeHistoryEntry[] = JSON.parse(stored);
        // Filter out old entries and entries for other gauges
        const cutoffTime = Date.now() - MAX_HISTORY_HOURS * 60 * 60 * 1000;
        const filtered = parsed.filter(
          (entry) => entry.timestamp > cutoffTime && entry.gaugeId === gaugeId
        );
        setHistory(filtered);
      }
    } catch (error) {
      console.warn('Error loading gauge history:', error);
      setHistory([]);
    }
  }, [gaugeId, MAX_HISTORY_HOURS]);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.warn('Error saving gauge history:', error);
    }
  }, [history]);

  const addReading = useCallback(
    (reading: GaugeReading) => {
      const now = Date.now();
      const newEntry: GaugeHistoryEntry = {
        gaugeId,
        reading,
        timestamp: now,
      };

      setHistory((prev) => {
        // Remove old entries and add new one
        const cutoffTime = now - MAX_HISTORY_HOURS * 60 * 60 * 1000;
        const filtered = prev.filter((entry) => entry.timestamp > cutoffTime);

        // Check if we already have a recent reading (avoid duplicates)
        const recentEntry = filtered
          .filter((entry) => entry.gaugeId === gaugeId)
          .sort((a, b) => b.timestamp - a.timestamp)[0];

        if (
          recentEntry &&
          now - recentEntry.timestamp < MIN_TREND_INTERVAL_MINUTES * 60 * 1000
        ) {
          // Too recent, just update the existing entry
          return filtered.map((entry) =>
            entry === recentEntry ? newEntry : entry
          );
        }

        // Add new entry
        return [...filtered, newEntry].sort(
          (a, b) => b.timestamp - a.timestamp
        );
      });
    },
    [gaugeId, MAX_HISTORY_HOURS, MIN_TREND_INTERVAL_MINUTES]
  );

  const getPreviousReading = useCallback((): GaugeReading | null => {
    const gaugeHistory = history
      .filter((entry) => entry.gaugeId === gaugeId)
      .sort((a, b) => b.timestamp - a.timestamp);

    // Return the second most recent reading (first is current)
    return gaugeHistory.length > 1 ? gaugeHistory[1].reading : null;
  }, [history, gaugeId]);

  const getReadingAge = useCallback(
    (reading: GaugeReading): number => {
      const entry = history.find(
        (h) =>
          h.gaugeId === gaugeId && h.reading.timestamp === reading.timestamp
      );
      return entry ? Date.now() - entry.timestamp : 0;
    },
    [history, gaugeId]
  );

  return {
    addReading,
    getPreviousReading,
    getReadingAge,
    historyCount: history.filter((h) => h.gaugeId === gaugeId).length,
  };
}
