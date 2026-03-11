import { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Link as MuiLink,
  Paper,
} from '@mui/material';

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

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
          color: 'text.secondary',
        }}
      >
        <Typography variant="body2" sx={{ mb: 1 }}>
          {fallbackLabel}
        </Typography>
        <MuiLink href={fallbackUrl} target="_blank" rel="noopener noreferrer">
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
      sx={{ width: '100%', height: 'auto', borderRadius: 1 }}
    />
  );
}

export function ForecastPanel() {
  const [tab, setTab] = useState<ForecastTab>('qpf');
  const [qpfDay, setQpfDay] = useState(0);
  const [observedPeriod, setObservedPeriod] = useState(0);

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="Forecast (QPF)" value="qpf" />
        <Tab label="Observed" value="observed" />
      </Tabs>

      <Box sx={{ flex: 1, overflow: 'auto', p: 1.5 }}>
        {tab === 'qpf' && (
          <>
            <Tabs
              value={qpfDay}
              onChange={(_, v) => setQpfDay(v)}
              variant="fullWidth"
              sx={{ mb: 1 }}
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
              sx={{ display: 'block', mt: 1, color: 'text.secondary' }}
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
              sx={{ mb: 1 }}
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
              sx={{ display: 'block', mt: 1, color: 'text.secondary' }}
            >
              Source: NWS Advanced Hydrologic Prediction Service
            </Typography>
          </>
        )}
      </Box>
    </Paper>
  );
}
