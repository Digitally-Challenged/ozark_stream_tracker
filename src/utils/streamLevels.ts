// src/utils/streamLevels.ts
import {
  LevelStatus,
  LevelTrend,
  TargetLevels,
  GaugeReading,
} from '../types/stream';
import { differenceInHours } from 'date-fns';
import { STREAM_LEVELS } from '../constants';
import { Theme } from '@mui/material/styles';

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
  const THRESHOLD = STREAM_LEVELS.CHANGE_THRESHOLD; // Minimum change to consider rising/falling

  if (Math.abs(difference) < THRESHOLD) return LevelTrend.Holding;
  return difference > 0 ? LevelTrend.Rising : LevelTrend.Falling;
};

export const getReadingFreshnessColor = (timestamp: string, theme: Theme): string => {
  const hours = differenceInHours(new Date(), new Date(timestamp));

  if (hours < STREAM_LEVELS.FRESHNESS_HOURS.VERY_FRESH) return theme.palette.success.main; // Fresh
  if (hours < STREAM_LEVELS.FRESHNESS_HOURS.FRESH) return theme.palette.info.main; // Recent
  if (hours < STREAM_LEVELS.FRESHNESS_HOURS.RECENT) return theme.palette.warning.main; // Stale
  return theme.palette.error.main; // Old
};

export const getLevelStatusColor = (status: LevelStatus, theme: Theme): string => {
  const alpha = theme.palette.mode === 'dark' ? '0.3' : '0.2';
  
  switch (status) {
    case LevelStatus.TooLow:
      return `rgba(${theme.palette.error.main.replace('#', '').match(/.{2}/g)?.map(hex => parseInt(hex, 16)).join(', ')}, ${alpha})`;
    case LevelStatus.Low:
      return `rgba(${theme.palette.warning.main.replace('#', '').match(/.{2}/g)?.map(hex => parseInt(hex, 16)).join(', ')}, ${alpha})`;
    case LevelStatus.Optimal:
      return `rgba(${theme.palette.success.main.replace('#', '').match(/.{2}/g)?.map(hex => parseInt(hex, 16)).join(', ')}, ${alpha})`;
    case LevelStatus.High:
      return `rgba(${theme.palette.info.main.replace('#', '').match(/.{2}/g)?.map(hex => parseInt(hex, 16)).join(', ')}, ${alpha})`;
    default:
      return 'transparent';
  }
};

export const getQualityColor = (quality: string, theme: Theme): string => {
  // Alpha value available for future use
  // const alpha = theme.palette.mode === 'dark' ? '0.2' : '0.1';
  
  switch (quality) {
    case 'A':
    case 'A+':
      return theme.palette.success.light + (theme.palette.mode === 'dark' ? '33' : '1A'); // 20% or 10% opacity
    case 'B':
    case 'B+':
      return theme.palette.info.light + (theme.palette.mode === 'dark' ? '33' : '1A');
    case 'C':
    case 'C+':
      return theme.palette.warning.light + (theme.palette.mode === 'dark' ? '33' : '1A');
    case 'D':
    case 'D+':
      return theme.palette.warning.dark + (theme.palette.mode === 'dark' ? '33' : '1A');
    case 'F':
      return theme.palette.error.light + (theme.palette.mode === 'dark' ? '33' : '1A');
    default:
      return 'transparent';
  }
};
