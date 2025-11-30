// src/components/common/StreamSkeleton.tsx
import { Box, Skeleton, keyframes } from '@mui/material';

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

interface StreamSkeletonProps {
  variant?: 'card' | 'row';
}

export function StreamSkeleton({ variant = 'card' }: StreamSkeletonProps) {
  if (variant === 'row') {
    return (
      <Box sx={{ display: 'flex', gap: 2, p: 2, alignItems: 'center' }}>
        <Skeleton variant="text" width={180} height={24} />
        <Skeleton variant="rounded" width={60} height={24} />
        <Skeleton variant="rounded" width={40} height={24} />
        <Skeleton variant="text" width={100} height={20} />
        <Skeleton variant="text" width={80} height={24} />
        <Skeleton variant="circular" width={32} height={32} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        p: 2,
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'divider',
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(255, 255, 255, 0.02)'
            : 'rgba(0, 0, 0, 0.02)',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Skeleton
          variant="text"
          width="60%"
          height={28}
          sx={{
            background: (theme) =>
              `linear-gradient(90deg, ${
                theme.palette.mode === 'dark'
                  ? 'rgba(255,255,255,0.08)'
                  : 'rgba(0,0,0,0.08)'
              } 25%, ${
                theme.palette.mode === 'dark'
                  ? 'rgba(255,255,255,0.15)'
                  : 'rgba(0,0,0,0.15)'
              } 50%, ${
                theme.palette.mode === 'dark'
                  ? 'rgba(255,255,255,0.08)'
                  : 'rgba(0,0,0,0.08)'
              } 75%)`,
            backgroundSize: '200% 100%',
            animation: `${shimmer} 1.5s infinite`,
          }}
        />
        <Skeleton variant="circular" width={32} height={32} />
      </Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Skeleton variant="rounded" width={60} height={24} />
        <Skeleton variant="rounded" width={40} height={24} />
      </Box>
      <Skeleton variant="text" width="40%" height={36} />
      <Skeleton variant="text" width="50%" height={20} sx={{ mt: 1 }} />
    </Box>
  );
}
