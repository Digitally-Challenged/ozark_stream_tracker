import { Box, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { WaterDrop, WbSunny } from '@mui/icons-material';
import { WeatherPeriod } from '../../services/nwsWeatherService';

interface WeatherForecastProps {
  periods: WeatherPeriod[];
}

function getRainColor(chance: number): string {
  if (chance >= 70) return '#1565c0';
  if (chance >= 40) return '#0288d1';
  if (chance >= 20) return '#4fc3f7';
  return '#9e9e9e';
}

function getRainLabel(chance: number): string {
  if (chance >= 70) return 'Likely';
  if (chance >= 40) return 'Chance';
  if (chance >= 20) return 'Slight';
  return 'Dry';
}

export function WeatherForecast({ periods }: WeatherForecastProps) {
  if (periods.length === 0) return null;

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: `repeat(${Math.min(periods.length, 5)}, 1fr)`,
        gap: 1,
      }}
    >
      {periods.map((period) => {
        const isRainy = period.precipChance >= 20;
        return (
          <Box
            key={period.name}
            sx={{
              textAlign: 'center',
              py: 1.5,
              px: 1,
              borderRadius: 2,
              bgcolor: (theme) =>
                isRainy
                  ? alpha(getRainColor(period.precipChance), 0.08)
                  : alpha(theme.palette.background.default, 0.5),
              border: (theme) =>
                `1px solid ${alpha(
                  isRainy
                    ? getRainColor(period.precipChance)
                    : theme.palette.divider,
                  isRainy ? 0.2 : 0.1
                )}`,
            }}
          >
            <Typography
              variant="caption"
              sx={{
                fontWeight: 700,
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.03em',
                display: 'block',
                mb: 0.75,
              }}
            >
              {period.name}
            </Typography>

            {isRainy ? (
              <WaterDrop
                sx={{
                  fontSize: 20,
                  color: getRainColor(period.precipChance),
                  mb: 0.25,
                }}
              />
            ) : (
              <WbSunny sx={{ fontSize: 20, color: '#ffa726', mb: 0.25 }} />
            )}

            <Typography
              variant="body2"
              sx={{
                fontWeight: 700,
                fontSize: '0.85rem',
                color: isRainy
                  ? getRainColor(period.precipChance)
                  : 'text.secondary',
                display: 'block',
              }}
            >
              {period.precipChance}%
            </Typography>

            <Typography
              variant="caption"
              sx={{
                fontSize: '0.55rem',
                color: 'text.disabled',
                fontWeight: 600,
                display: 'block',
                mb: 0.5,
              }}
            >
              {getRainLabel(period.precipChance)}
            </Typography>

            <Typography
              variant="caption"
              sx={{
                fontSize: '0.65rem',
                color: 'text.secondary',
                display: 'block',
              }}
            >
              {period.temperature}°F
            </Typography>

            <Typography
              variant="caption"
              sx={{
                fontSize: '0.5rem',
                color: 'text.disabled',
                display: 'block',
                mt: 0.25,
                lineHeight: 1.3,
              }}
            >
              {period.shortForecast}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}
