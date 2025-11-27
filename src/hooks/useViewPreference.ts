// src/hooks/useViewPreference.ts
import { useState, useEffect, useCallback } from 'react';

export type ViewMode = 'table' | 'cards';

const STORAGE_KEY = 'ozark-stream-tracker-view-mode';
const MOBILE_BREAKPOINT = 768;

export function useViewPreference(): {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  isManualOverride: boolean;
} {
  const [manualMode, setManualMode] = useState<ViewMode | null>(() => {
    if (typeof window === 'undefined') return null;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'table' || stored === 'cards' ? stored : null;
  });

  const [windowWidth, setWindowWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth : MOBILE_BREAKPOINT + 1
  );

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const responsiveDefault: ViewMode = windowWidth < MOBILE_BREAKPOINT ? 'cards' : 'table';
  const viewMode = manualMode ?? responsiveDefault;

  const setViewMode = useCallback((mode: ViewMode) => {
    setManualMode(mode);
    localStorage.setItem(STORAGE_KEY, mode);
  }, []);

  return {
    viewMode,
    setViewMode,
    isManualOverride: manualMode !== null,
  };
}
