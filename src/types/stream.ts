// src/types/stream.ts
export enum LevelTrend {
  Rising = 'rise',
  Falling = 'fall',
  Holding = 'hold',
  None = 'none'
}

export enum LevelStatus {
  TooLow = 'X',
  Low = 'L',
  Optimal = 'O',
  High = 'H'
}

export interface GaugeReading {
  value: number;
  timestamp: string;
}

export interface StreamGauge {
  name: string;
  id: string;
  url: string;
}

export interface TargetLevels {
  tooLow: number;
  optimal: number;
  high: number;
}

export interface StreamData {
  name: string;
  rating: string;
  size: 'XS' | 'VS' | 'S' | 'M' | 'L' | 'H' | 'DC' | 'A';
  gauge: StreamGauge;
  quality: 'A' | 'A+' | 'B' | 'B+' | 'C' | 'C+' | 'D' | 'D+' | 'F';
  targetLevels: TargetLevels;
  currentLevel?: {
    status: LevelStatus;
    trend: LevelTrend;
    reading?: GaugeReading;
  };
}