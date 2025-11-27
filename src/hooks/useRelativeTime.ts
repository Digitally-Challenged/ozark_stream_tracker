import { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';

/**
 * Custom hook that provides a dynamically updating relative time string
 * @param timestamp - The timestamp to calculate relative time from
 * @param updateInterval - How often to update the relative time (in milliseconds)
 * @returns The formatted relative time string that updates automatically
 */
export function useRelativeTime(timestamp: string | undefined, updateInterval: number = 60000) {
  const [relativeTime, setRelativeTime] = useState<string>('');

  useEffect(() => {
    if (!timestamp) {
      setRelativeTime('');
      return;
    }

    const updateRelativeTime = () => {
      try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) {
          setRelativeTime('Invalid date');
          return;
        }
        setRelativeTime(formatDistanceToNow(date, { addSuffix: true }));
      } catch {
        setRelativeTime('Invalid date');
      }
    };

    // Update immediately
    updateRelativeTime();

    // Set up interval to update periodically
    const intervalId = setInterval(updateRelativeTime, updateInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [timestamp, updateInterval]);

  return relativeTime;
}