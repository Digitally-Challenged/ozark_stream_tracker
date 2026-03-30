// src/utils/floatOutlook.ts
import { TargetLevels } from '../types/stream';
import { WeatherPeriod } from '../services/nwsWeatherService';

export type OutlookRating =
  | 'too-low'
  | 'improving'
  | 'likely-runnable'
  | 'runnable'
  | 'high-water'
  | 'declining';

export interface DayOutlook {
  day: string;
  precipChance: number;
  shortForecast: string;
  rating: OutlookRating;
  label: string;
}

export interface StreamOutlook {
  streamName: string;
  currentStatus: string;
  gapToOptimal: number | null;
  days: DayOutlook[];
  summary: string;
}

const OUTLOOK_LABELS: Record<OutlookRating, string> = {
  'too-low': 'Too Low',
  improving: 'Improving',
  'likely-runnable': 'Likely Runnable',
  runnable: 'Runnable',
  'high-water': 'High Water',
  declining: 'Declining',
};

const OUTLOOK_COLORS: Record<OutlookRating, string> = {
  'too-low': '#d32f2f',
  improving: '#ed6c02',
  'likely-runnable': '#0288d1',
  runnable: '#2e7d32',
  'high-water': '#1565c0',
  declining: '#ed6c02',
};

export { OUTLOOK_LABELS, OUTLOOK_COLORS };

function getRainIntensity(chance: number, shortForecast: string): number {
  const lower = shortForecast.toLowerCase();
  const isHeavy =
    lower.includes('thunderstorm') ||
    lower.includes('heavy') ||
    lower.includes('showers and');
  const isModerate =
    lower.includes('showers') ||
    lower.includes('rain likely') ||
    lower.includes('rain showers');

  if (chance >= 70 && isHeavy) return 3;
  if (chance >= 70) return 2.5;
  if (chance >= 40 && isHeavy) return 2;
  if (chance >= 40) return 1.5;
  if (chance >= 20 && isModerate) return 1;
  if (chance >= 20) return 0.5;
  return 0;
}

export function computeStreamOutlook(
  streamName: string,
  currentStage: number | null,
  targetLevels: TargetLevels,
  weatherPeriods: WeatherPeriod[]
): StreamOutlook {
  const gap =
    currentStage !== null ? targetLevels.optimal - currentStage : null;
  const isCurrentlyRunnable =
    currentStage !== null &&
    currentStage >= targetLevels.optimal &&
    currentStage < targetLevels.high;
  const isCurrentlyHigh =
    currentStage !== null && currentStage >= targetLevels.high;
  const optimalRange = targetLevels.high - targetLevels.optimal;
  const normalizedGap =
    gap !== null && optimalRange > 0 ? gap / optimalRange : null;

  let cumulativeRainImpact = 0;

  const days: DayOutlook[] = weatherPeriods.map((period) => {
    const intensity = getRainIntensity(
      period.precipChance,
      period.shortForecast
    );
    cumulativeRainImpact += intensity;

    // Without rain, levels drop ~0.3 "units" per dry day
    if (intensity === 0) {
      cumulativeRainImpact = Math.max(0, cumulativeRainImpact - 0.3);
    }

    let rating: OutlookRating;

    if (isCurrentlyHigh) {
      rating =
        intensity > 1
          ? 'high-water'
          : cumulativeRainImpact > 2
            ? 'high-water'
            : 'runnable';
    } else if (isCurrentlyRunnable) {
      if (intensity > 2) {
        rating = 'high-water';
      } else if (intensity === 0 && cumulativeRainImpact < 0.5) {
        rating = 'declining';
      } else {
        rating = 'runnable';
      }
    } else if (normalizedGap !== null) {
      // Below optimal — can rain close the gap?
      if (normalizedGap <= 0.1 && cumulativeRainImpact >= 1) {
        rating = 'runnable';
      } else if (normalizedGap <= 0.3 && cumulativeRainImpact >= 2) {
        rating = 'likely-runnable';
      } else if (cumulativeRainImpact >= 3) {
        rating = 'likely-runnable';
      } else if (cumulativeRainImpact >= 1) {
        rating = 'improving';
      } else {
        rating = 'too-low';
      }
    } else {
      rating = 'too-low';
    }

    return {
      day: period.name,
      precipChance: period.precipChance,
      shortForecast: period.shortForecast,
      rating,
      label: OUTLOOK_LABELS[rating],
    };
  });

  // Generate summary
  let summary: string;
  const hasHeavyRain = weatherPeriods.some(
    (p) =>
      p.precipChance >= 60 && p.shortForecast.toLowerCase().includes('thunder')
  );
  const hasAnyRain = weatherPeriods.some((p) => p.precipChance >= 40);
  const bestDay = days.reduce<DayOutlook | null>(
    (best, d) =>
      d.rating === 'runnable' || d.rating === 'likely-runnable'
        ? best === null
          ? d
          : best
        : best,
    null
  );

  if (isCurrentlyRunnable) {
    if (hasHeavyRain) {
      summary =
        'Currently runnable. Heavy rain may push to high water — check before heading out.';
    } else if (!hasAnyRain) {
      summary = 'Currently runnable but levels will drop without rain.';
    } else {
      summary = 'Currently runnable. Rain should maintain or improve levels.';
    }
  } else if (bestDay) {
    summary = `${hasHeavyRain ? 'Heavy rain' : 'Rain'} expected — conditions likely improve by ${bestDay.day}.`;
  } else if (hasAnyRain) {
    summary =
      'Rain in the forecast but may not be enough to reach optimal. Keep watching.';
  } else {
    summary = 'No significant rain expected. Levels likely to remain low.';
  }

  const currentStatus =
    currentStage === null
      ? 'Unknown'
      : isCurrentlyHigh
        ? 'High'
        : isCurrentlyRunnable
          ? 'Optimal'
          : currentStage >= targetLevels.tooLow
            ? 'Low'
            : 'Too Low';

  return {
    streamName,
    currentStatus,
    gapToOptimal: gap !== null && gap > 0 ? gap : null,
    days,
    summary,
  };
}
