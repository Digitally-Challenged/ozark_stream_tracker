import { GaugeReading } from '../types/stream';

interface TurnerBendData {
  level: number;
  timestamp: string;
  description?: string;
}

export class TurnerBendScraper {
  private static readonly API_URL =
    import.meta.env.VITE_API_URL || '/api/turner-bend/current';
  private static readonly CACHE_KEY = 'turner-bend-gauge-data';
  private static readonly CACHE_DURATION = 15 * 60 * 1000; // 15 minutes

  static async fetchGaugeData(): Promise<GaugeReading | null> {
    try {
      // Check cache first
      const cached = this.getCachedData();
      if (cached) {
        return cached;
      }

      // Try to fetch from backend API - NO FALLBACK TO MOCK DATA
      const response = await fetch(this.API_URL, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
        // Add timeout to fail fast if server is down
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        throw new Error(
          `Turner Bend API error: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();

      if (!data || typeof data.level !== 'number') {
        throw new Error('Invalid Turner Bend data format received');
      }

      const reading = this.parseToGaugeReading(data);
      this.setCachedData(reading);
      return reading;
    } catch (error) {
      console.error('Error fetching Turner Bend gauge data:', error);
      return null;
    }
  }

  private static parseToGaugeReading(data: TurnerBendData): GaugeReading {
    return {
      value: data.level,
      unit: 'ft',
      dateTime: data.timestamp,
      timestamp: data.timestamp,
      qualifiers: data.description ? [data.description] : [],
    };
  }

  private static getCachedData(): GaugeReading | null {
    try {
      const cached = localStorage.getItem(this.CACHE_KEY);
      if (!cached) return null;

      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;

      if (age > this.CACHE_DURATION) {
        localStorage.removeItem(this.CACHE_KEY);
        return null;
      }

      return data;
    } catch {
      return null;
    }
  }

  private static setCachedData(data: GaugeReading): void {
    try {
      localStorage.setItem(
        this.CACHE_KEY,
        JSON.stringify({ data, timestamp: Date.now() })
      );
    } catch (error) {
      console.error('Error caching Turner Bend data:', error);
    }
  }
}
