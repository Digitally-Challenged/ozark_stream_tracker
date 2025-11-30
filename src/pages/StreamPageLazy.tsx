import { lazy, Suspense } from 'react';
import { Box, CircularProgress, Container } from '@mui/material';

const StreamPage = lazy(() => import('./StreamPage'));

function LoadingFallback() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh',
        }}
      >
        <CircularProgress />
      </Box>
    </Container>
  );
}

export function StreamPageLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <StreamPage />
    </Suspense>
  );
}
