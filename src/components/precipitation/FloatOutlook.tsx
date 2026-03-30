// src/components/precipitation/FloatOutlook.tsx
import { Box, Typography, Chip } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { WaterDrop, WbSunny, Lightbulb } from '@mui/icons-material';
import { StreamOutlook, OUTLOOK_COLORS } from '../../utils/floatOutlook';

interface FloatOutlookProps {
  outlooks: StreamOutlook[];
}

export function FloatOutlook({ outlooks }: FloatOutlookProps) {
  if (outlooks.length === 0) return null;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {outlooks.map((outlook) => (
        <Box key={outlook.streamName}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              mb: 1,
            }}
          >
            <Typography
              variant="caption"
              sx={{ fontWeight: 700, fontSize: '0.8rem' }}
            >
              {outlook.streamName}
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: 'text.secondary', fontSize: '0.65rem' }}
            >
              Now: {outlook.currentStatus}
              {outlook.gapToOptimal !== null &&
                ` — need +${outlook.gapToOptimal.toFixed(1)} ft`}
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: `repeat(${Math.min(outlook.days.length, 5)}, 1fr)`,
              gap: 0.75,
              mb: 1.5,
            }}
          >
            {outlook.days.map((day) => {
              const color = OUTLOOK_COLORS[day.rating];
              const isRainy = day.precipChance >= 20;
              return (
                <Box
                  key={day.day}
                  sx={{
                    textAlign: 'center',
                    py: 1,
                    px: 0.5,
                    borderRadius: 1.5,
                    bgcolor: alpha(color, 0.08),
                    border: `1px solid ${alpha(color, 0.2)}`,
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 700,
                      fontSize: '0.6rem',
                      textTransform: 'uppercase',
                      display: 'block',
                      mb: 0.5,
                    }}
                  >
                    {day.day}
                  </Typography>
                  {isRainy ? (
                    <WaterDrop
                      sx={{ fontSize: 16, color: '#0288d1', mb: 0.25 }}
                    />
                  ) : (
                    <WbSunny
                      sx={{ fontSize: 16, color: '#ffa726', mb: 0.25 }}
                    />
                  )}
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      fontSize: '0.55rem',
                      color: 'text.disabled',
                      mb: 0.5,
                    }}
                  >
                    {day.precipChance}% rain
                  </Typography>
                  <Chip
                    label={day.label}
                    size="small"
                    sx={{
                      height: 18,
                      fontSize: '0.5rem',
                      fontWeight: 700,
                      bgcolor: alpha(color, 0.15),
                      color,
                      border: `1px solid ${alpha(color, 0.3)}`,
                      '& .MuiChip-label': { px: 0.75 },
                    }}
                  />
                </Box>
              );
            })}
          </Box>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 0.75,
              py: 1,
              px: 1.5,
              borderRadius: 1.5,
              bgcolor: (theme) => alpha(theme.palette.info.main, 0.06),
              border: (theme) =>
                `1px solid ${alpha(theme.palette.info.main, 0.12)}`,
            }}
          >
            <Lightbulb
              sx={{ fontSize: 14, color: '#ffa726', mt: 0.25, flexShrink: 0 }}
            />
            <Typography
              variant="caption"
              sx={{
                fontSize: '0.7rem',
                color: 'text.secondary',
                lineHeight: 1.5,
              }}
            >
              {outlook.summary}
            </Typography>
          </Box>
        </Box>
      ))}
    </Box>
  );
}
