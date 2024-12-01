import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import { Stream, LevelTrend } from '../../types/stream';
import { useStreamGauge } from '../../hooks/useStreamGauge';
import { useTheme } from '@mui/material';

interface StreamTrendProps {
  stream: Stream;
  size?: number;
}

const StreamTrend = ({ stream, size = 20 }: StreamTrendProps) => {
  const { currentLevel, loading, error } = useStreamGauge(stream);
  const theme = useTheme();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error</div>;
  if (!currentLevel?.trend || currentLevel.trend === LevelTrend.None) return null;

  const getTrendIcon = () => {
    const iconProps = {
      size,
      strokeWidth: 2,
      style: {
        color: currentLevel.trend === LevelTrend.Rising ? theme.palette.success.main :
              currentLevel.trend === LevelTrend.Falling ? theme.palette.error.main :
              theme.palette.text.secondary
      }
    };

    switch (currentLevel.trend) {
      case LevelTrend.Rising:
        return <ArrowUp {...iconProps} />;
      case LevelTrend.Falling:
        return <ArrowDown {...iconProps} />;
      case LevelTrend.Holding:
        return <Minus {...iconProps} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {getTrendIcon()}
    </div>
  );
};

export default StreamTrend;