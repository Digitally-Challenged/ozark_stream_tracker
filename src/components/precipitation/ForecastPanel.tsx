import { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Link as MuiLink,
  useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { CloudOff } from '@mui/icons-material';
import { glassmorphism } from '../../theme/waterTheme';

type ForecastTab = 'qpf' | 'observed';

const QPF_IMAGES = [
  {
    label: 'Day 1',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_94qwbg.gif',
  },
  {
    label: 'Day 2',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_98qwbg.gif',
  },
  {
    label: 'Day 3',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_99qwbg.gif',
  },
];

function getObservedUrl(period: string): string {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `https://water.weather.gov/precip/downloads/${yyyy}/${mm}/${dd}/nws_precip_${period}_observed.png`;
}

const OBSERVED_IMAGES = [
  { label: '1 Day', period: 'last24hrs' },
  { label: '2 Day', period: 'last48hrs' },
  { label: '7 Day', period: 'last7days' },
];

function ImageWithFallback({
  src,
  alt,
  fallbackUrl,
  fallbackLabel,
}: {
  src: string;
  alt: string;
  fallbackUrl: string;
  fallbackLabel: string;
}) {
  const [error, setError] = useState(false);
  const theme = useTheme();

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          py: 6,
          px: 2,
          borderRadius: 2,
          border: `1px dashed ${alpha(theme.palette.text.secondary, 0.3)}`,
          background: alpha(theme.palette.background.default, 0.5),
        }}
      >
        <CloudOff
          sx={{
            fontSize: 36,
            color: alpha(theme.palette.text.secondary, 0.4),
            mb: 1.5,
          }}
        />
        <Typography
          variant="body2"
          sx={{ mb: 1, color: 'text.secondary', textAlign: 'center' }}
        >
          {fallbackLabel}
        </Typography>
        <MuiLink
          href={fallbackUrl}
          target="_blank"
          rel="noopener noreferrer"
          sx={{
            background: 'linear-gradient(135deg, #30cfd0, #330867)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 600,
            fontSize: '0.85rem',
          }}
        >
          View on source site
        </MuiLink>
      </Box>
    );
  }

  return (
    <Box
      component="img"
      src={src}
      alt={alt}
      onError={() => setError(true)}
      sx={{
        width: '100%',
        height: 'auto',
        borderRadius: 2,
        border: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
        boxShadow: `0 4px 12px ${alpha('#000', 0.15)}`,
      }}
    />
  );
}

export function ForecastPanel() {
  const [tab, setTab] = useState<ForecastTab>('qpf');
  const [qpfDay, setQpfDay] = useState(0);
  const [observedPeriod, setObservedPeriod] = useState(0);
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const glass = isDark ? glassmorphism.dark : glassmorphism.light;

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        ...glass,
        borderRadius: 0,
        borderLeft: isDark
          ? `1px solid ${alpha('#30cfd0', 0.2)}`
          : `1px solid ${alpha('#000', 0.08)}`,
      }}
    >
      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        variant="fullWidth"
        sx={{
          minHeight: 48,
          '& .MuiTabs-indicator': {
            height: 3,
            borderRadius: '3px 3px 0 0',
            background: 'linear-gradient(90deg, #30cfd0, #330867)',
          },
          '& .MuiTab-root': {
            fontWeight: 700,
            letterSpacing: '0.05em',
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            minHeight: 48,
            transition: 'color 0.3s',
          },
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
        }}
      >
        <Tab label="Forecast (QPF)" value="qpf" />
        <Tab label="Observed" value="observed" />
      </Tabs>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {tab === 'qpf' && (
          <>
            <Tabs
              value={qpfDay}
              onChange={(_, v) => setQpfDay(v)}
              variant="fullWidth"
              sx={{
                mb: 1.5,
                minHeight: 36,
                '& .MuiTabs-indicator': { display: 'none' },
                '& .MuiTab-root': {
                  minHeight: 36,
                  borderRadius: 2,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  mx: 0.25,
                  transition: 'all 0.2s',
                  '&.Mui-selected': {
                    background: alpha(theme.palette.primary.main, 0.15),
                    color: theme.palette.primary.main,
                  },
                },
              }}
            >
              {QPF_IMAGES.map((img, i) => (
                <Tab key={img.label} label={img.label} value={i} />
              ))}
            </Tabs>
            <ImageWithFallback
              src={QPF_IMAGES[qpfDay].url}
              alt={`QPF Forecast ${QPF_IMAGES[qpfDay].label}`}
              fallbackUrl="https://www.wpc.ncep.noaa.gov/qpf/qpf2.shtml"
              fallbackLabel="Forecast image unavailable"
            />
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1.5,
                pl: 1,
                borderLeft: `2px solid ${alpha('#30cfd0', 0.5)}`,
                color: 'text.secondary',
                fontStyle: 'italic',
              }}
            >
              Source: NOAA Weather Prediction Center
            </Typography>
          </>
        )}

        {tab === 'observed' && (
          <>
            <Tabs
              value={observedPeriod}
              onChange={(_, v) => setObservedPeriod(v)}
              variant="fullWidth"
              sx={{
                mb: 1.5,
                minHeight: 36,
                '& .MuiTabs-indicator': { display: 'none' },
                '& .MuiTab-root': {
                  minHeight: 36,
                  borderRadius: 2,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  mx: 0.25,
                  transition: 'all 0.2s',
                  '&.Mui-selected': {
                    background: alpha(theme.palette.info.main, 0.15),
                    color: theme.palette.info.main,
                  },
                },
              }}
            >
              {OBSERVED_IMAGES.map((img, i) => (
                <Tab key={img.label} label={img.label} value={i} />
              ))}
            </Tabs>
            <ImageWithFallback
              src={getObservedUrl(OBSERVED_IMAGES[observedPeriod].period)}
              alt={`Observed precipitation ${OBSERVED_IMAGES[observedPeriod].label}`}
              fallbackUrl="https://water.weather.gov/precip/"
              fallbackLabel="Observed precipitation image unavailable"
            />
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1.5,
                pl: 1,
                borderLeft: `2px solid ${alpha(theme.palette.info.main, 0.5)}`,
                color: 'text.secondary',
                fontStyle: 'italic',
              }}
            >
              Source: NWS Advanced Hydrologic Prediction Service
            </Typography>
          </>
        )}
      </Box>
    </Box>
  );
}
