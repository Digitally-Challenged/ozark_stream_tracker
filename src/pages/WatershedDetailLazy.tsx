import { lazy, Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';

const WatershedDetailPage = lazy(() => import('./WatershedDetailPage'));

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

export function WatershedDetailLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <WatershedDetailPage />
    </Suspense>
  );
}
