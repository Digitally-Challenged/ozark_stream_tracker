import { LevelTrend } from '../types/stream';
import { TrendingUp, TrendingDown, HorizontalRule } from '@mui/icons-material';
import { SvgIconComponent } from '@mui/icons-material';

export interface TrendInfo {
  icon: SvgIconComponent;
  label: string;
  muiColor: string;
}

export function getTrendLabel(trend: LevelTrend): string | null {
  switch (trend) {
    case LevelTrend.Rising:
      return 'Rising';
    case LevelTrend.Falling:
      return 'Falling';
    case LevelTrend.Holding:
      return 'Stable';
    default:
      return null;
  }
}

export function getTrendMuiColor(trend: LevelTrend): string | null {
  switch (trend) {
    case LevelTrend.Rising:
      return 'success.main';
    case LevelTrend.Falling:
      return 'error.main';
    case LevelTrend.Holding:
      return 'warning.main';
    default:
      return null;
  }
}

export function getTrendInfo(trend: LevelTrend): TrendInfo | null {
  if (trend === LevelTrend.None) return null;

  const label = getTrendLabel(trend);
  const muiColor = getTrendMuiColor(trend);
  if (!label || !muiColor) return null;

  const icons: Record<string, SvgIconComponent> = {
    [LevelTrend.Rising]: TrendingUp,
    [LevelTrend.Falling]: TrendingDown,
    [LevelTrend.Holding]: HorizontalRule,
  };

  return {
    icon: icons[trend],
    label,
    muiColor,
  };
}
