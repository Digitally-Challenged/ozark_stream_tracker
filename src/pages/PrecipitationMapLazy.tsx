import { lazy, Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';

const PrecipitationMap = lazy(() => import('./PrecipitationMap'));

function LoadingFallback() {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flex: 1,
      }}
    >
      <CircularProgress />
    </Box>
  );
}

export function PrecipitationMapLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <PrecipitationMap />
    </Suspense>
  );
}
