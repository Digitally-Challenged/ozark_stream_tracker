import { alpha } from '@mui/material/styles';

export const waterGradients = {
  // Water depth gradients
  shallow: 'linear-gradient(135deg, #74ebd5 0%, #9face6 100%)',
  medium: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  deep: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
  rapid: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  
  // Time-based gradients
  dawn: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  day: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
  dusk: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
  night: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  
  // Condition gradients
  optimal: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
  warning: 'linear-gradient(135deg, #f2994a 0%, #f2c94c 100%)',
  danger: 'linear-gradient(135deg, #e44d26 0%, #f09819 100%)',
};

export const glassmorphism = {
  light: {
    background: alpha('#ffffff', 0.7),
    backdropFilter: 'blur(10px)',
    border: `1px solid ${alpha('#ffffff', 0.2)}`,
    boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
  },
  dark: {
    background: alpha('#000000', 0.4),
    backdropFilter: 'blur(10px)',
    border: `1px solid ${alpha('#ffffff', 0.1)}`,
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
  },
  colored: (color: string, opacity: number = 0.1) => ({
    background: alpha(color, opacity),
    backdropFilter: 'blur(10px)',
    border: `1px solid ${alpha(color, 0.2)}`,
    boxShadow: `0 8px 32px 0 ${alpha(color, 0.15)}`,
  }),
};

export const animations = {
  float: `
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
    }
  `,
  wave: `
    @keyframes wave {
      0% { transform: translateX(0) translateZ(0) scaleY(1); }
      50% { transform: translateX(-25%) translateZ(0) scaleY(0.55); }
      100% { transform: translateX(-50%) translateZ(0) scaleY(1); }
    }
  `,
  ripple: `
    @keyframes ripple {
      0% {
        transform: scale(1);
        opacity: 1;
      }
      100% {
        transform: scale(4);
        opacity: 0;
      }
    }
  `,
  shimmer: `
    @keyframes shimmer {
      0% { background-position: -1000px 0; }
      100% { background-position: 1000px 0; }
    }
  `,
  liquidFill: `
    @keyframes liquidFill {
      0% { transform: translateY(100%); }
      100% { transform: translateY(var(--fill-level, 50%)); }
    }
  `,
};

export const shadows = {
  glass: {
    sm: '0 2px 8px 0 rgba(31, 38, 135, 0.1)',
    md: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
    lg: '0 12px 48px 0 rgba(31, 38, 135, 0.2)',
  },
  glow: {
    blue: '0 0 20px rgba(74, 235, 213, 0.5)',
    green: '0 0 20px rgba(56, 239, 125, 0.5)',
    yellow: '0 0 20px rgba(242, 201, 76, 0.5)',
    red: '0 0 20px rgba(240, 87, 108, 0.5)',
  },
  elevation: {
    1: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    2: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    3: '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
    4: '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
    5: '0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)',
  },
};