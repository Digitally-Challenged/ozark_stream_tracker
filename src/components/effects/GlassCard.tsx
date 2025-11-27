// React import not needed in modern React
import { Box, BoxProps } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { glassmorphism } from '../../theme/waterTheme';

interface GlassCardProps extends BoxProps {
  variant?: 'light' | 'dark' | 'auto';
  blur?: number;
  opacity?: number;
  gradient?: string;
  hover?: boolean;
}

export function GlassCard({
  children,
  variant = 'auto',
  blur = 10,
  opacity,
  gradient,
  hover = true,
  sx,
  ...props
}: GlassCardProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  
  const glassVariant = variant === 'auto' ? (isDark ? 'dark' : 'light') : variant;
  const glassStyle = glassmorphism[glassVariant];
  
  const customOpacity = opacity ?? (isDark ? 0.4 : 0.7);
  
  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 3,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        ...glassStyle,
        background: gradient || glassStyle.background.replace(/[\d.]+\)$/, `${customOpacity})`),
        backdropFilter: `blur(${blur}px)`,
        '&::before': gradient ? {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: gradient,
          opacity: 0.1,
          zIndex: -1,
        } : {},
        ...(hover && {
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme.shadows[8],
            '&::after': {
              opacity: 1,
            },
          },
        }),
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: `linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
          )`,
          transform: 'rotate(45deg)',
          transition: 'opacity 0.3s',
          opacity: 0,
          pointerEvents: 'none',
        },
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  );
}