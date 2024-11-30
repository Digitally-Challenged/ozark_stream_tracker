export interface GaugeReading {
  value: number;
  timestamp: string;
}

export enum LevelTrend {
  Rising = 'rise',
  Falling = 'fall',
  Holding = 'hold',
  None = 'none'
}

export interface Stream {
  id?: string;
  name: string;
  rating: string;
  size: string;
  gauge: {
    name: string;
    id: string;
    url: string;
  };
  quality: string;
  targetLevels: {
    tooLow: number;
    optimal: number;
    high: number;
  };
  currentLevel?: {
    status: string;  // 'X', 'L', 'O', 'H'
    trend: LevelTrend;
  };
}

export interface StreamData extends Stream {
  currentFlow?: number;
  temperature?: number;
  status?: string;
  lastUpdated?: string;
  waterQuality?: {
    ph: number;
    turbidity: number;
    dissolvedOxygen: number;
  };
}