// src/utils/streamLevels.ts
import { LevelStatus, LevelTrend, TargetLevels, GaugeReading } from '../types/stream';
import { differenceInHours } from 'date-fns';

export const determineLevel = (
  reading: number,
  targetLevels: TargetLevels
): LevelStatus => {
  if (reading < targetLevels.tooLow) return LevelStatus.TooLow;
  if (reading < targetLevels.optimal) return LevelStatus.Low;
  if (reading < targetLevels.high) return LevelStatus.Optimal;
  return LevelStatus.High;
};

export const determineTrend = (
  current: GaugeReading,
  previous?: GaugeReading
): LevelTrend => {
  if (!previous) return LevelTrend.None;
  
  const difference = current.value - previous.value;
  const THRESHOLD = 0.1; // Minimum change to consider rising/falling
  
  if (Math.abs(difference) < THRESHOLD) return LevelTrend.Holding;
  return difference > 0 ? LevelTrend.Rising : LevelTrend.Falling;
};

export const getReadingFreshnessClass = (timestamp: string): string => {
  const hours = differenceInHours(new Date(), new Date(timestamp));
  
  if (hours < 1.5) return 'text-green-600'; // Fresh
  if (hours < 3.0) return 'text-blue-600';  // Recent
  if (hours < 10.0) return 'text-yellow-600'; // Stale
  return 'text-red-600'; // Old
};

export const getLevelStatusClass = (status: LevelStatus): string => {
  switch (status) {
    case LevelStatus.TooLow: return 'bg-red-500/20';
    case LevelStatus.Low: return 'bg-yellow-500/20';
    case LevelStatus.Optimal: return 'bg-green-500/20';
    case LevelStatus.High: return 'bg-blue-500/20';
    default: return '';
  }
};

export const getQualityClass = (quality: string): string => {
  switch (quality) {
    case 'A':
    case 'A+': return 'bg-green-100';
    case 'B':
    case 'B+': return 'bg-blue-100';
    case 'C':
    case 'C+': return 'bg-yellow-100';
    case 'D':
    case 'D+': return 'bg-orange-100';
    case 'F': return 'bg-red-100';
    default: return '';
  }
};