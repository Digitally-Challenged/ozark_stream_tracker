# Stylish UI Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Ozark Stream Tracker UI with polished visual enhancements that create a premium, water-themed experience without major architectural changes.

**Architecture:** We'll add skeleton loaders for polish, a live data indicator for real-time feedback, liquid fill bars for visual water level representation, and enhanced glassmorphism effects. All changes use existing MUI sx prop patterns and leverage the pre-built `waterTheme.ts` utilities.

**Tech Stack:** React 18, Material-UI 5, Emotion (CSS-in-JS), existing waterTheme.ts animations and glassmorphism utilities

---

## Phase 1: Loading States Polish (Quick Wins)

### Task 1: Create Skeleton Loading Component

**Files:**

- Create: `src/components/common/StreamSkeleton.tsx`

**Step 1: Create the StreamSkeleton component**

```tsx
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
```

**Step 2: Verify the file compiles**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/common/StreamSkeleton.tsx
git commit -m "feat: add shimmer skeleton loading component"
```

---

### Task 2: Integrate Skeleton into StreamCard

**Files:**

- Modify: `src/components/streams/StreamCard.tsx:85-87`

**Step 1: Import StreamSkeleton at the top of the file**

Add this import after the existing imports:

```tsx
import { StreamSkeleton } from '../common/StreamSkeleton';
```

**Step 2: Replace the loading state text with skeleton**

Find this block (around line 85-87):

```tsx
          {loading ? (
            <Typography color="text.secondary">Loading...</Typography>
          ) : error ? (
```

Replace with:

```tsx
          {loading ? (
            <Box sx={{ mt: 1 }}>
              <Skeleton variant="text" width="60%" height={36} />
              <Skeleton variant="text" width="40%" height={20} sx={{ mt: 0.5 }} />
            </Box>
          ) : error ? (
```

**Step 3: Add Skeleton import from MUI**

Find the MUI imports at the top:

```tsx
import {
  Card,
  CardContent,
  CardActionArea,
  Box,
  Typography,
  useTheme,
} from '@mui/material';
```

Add `Skeleton` to the import:

```tsx
import {
  Card,
  CardContent,
  CardActionArea,
  Box,
  Typography,
  useTheme,
  Skeleton,
} from '@mui/material';
```

**Step 4: Verify the file compiles**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 5: Test visually**

Run: `npm run dev`
Verify: Stream cards show skeleton animation while loading instead of "Loading..." text

**Step 6: Commit**

```bash
git add src/components/streams/StreamCard.tsx
git commit -m "feat: add skeleton loading state to StreamCard"
```

---

### Task 3: Integrate Skeleton into StreamTableRow

**Files:**

- Modify: `src/components/streams/StreamTableRow.tsx:146-163`

**Step 1: Add Skeleton import**

Find the MUI imports at the top and add `Skeleton`:

```tsx
import {
  TableRow,
  TableCell,
  Tooltip,
  useTheme,
  Link,
  Typography,
  Box,
  Skeleton,
} from '@mui/material';
```

**Step 2: Replace loading text in Current Reading cell**

Find the loading state (around line 154):

```tsx
        ) : loading ? (
          'Loading...'
        ) : error ? (
```

Replace with:

```tsx
        ) : loading ? (
          <Skeleton variant="text" width={80} height={24} />
        ) : error ? (
```

**Step 3: Replace loading text in Current Level cell**

Find this block (around line 200):

```tsx
        {loading ? (
          'Loading...'
        ) : error ? (
```

Replace with:

```tsx
        {loading ? (
          <Skeleton variant="circular" width={24} height={24} />
        ) : error ? (
```

**Step 4: Replace loading text in Trend cell**

Find this block (around line 215):

```tsx
        {loading ? (
          'Loading...'
        ) : error ? (
```

Replace with:

```tsx
        {loading ? (
          <Skeleton variant="circular" width={20} height={20} />
        ) : error ? (
```

**Step 5: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 6: Commit**

```bash
git add src/components/streams/StreamTableRow.tsx
git commit -m "feat: add skeleton loading states to StreamTableRow"
```

---

## Phase 2: Live Data Indicator

### Task 4: Create Live Indicator Component

**Files:**

- Create: `src/components/common/LiveIndicator.tsx`

**Step 1: Create the LiveIndicator component**

```tsx
// src/components/common/LiveIndicator.tsx
import { Box, Typography, keyframes, useTheme } from '@mui/material';
import { FiberManualRecord } from '@mui/icons-material';

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.9);
  }
`;

const glow = keyframes`
  0%, 100% {
    box-shadow: 0 0 4px currentColor;
  }
  50% {
    box-shadow: 0 0 12px currentColor, 0 0 20px currentColor;
  }
`;

interface LiveIndicatorProps {
  isLive?: boolean;
  lastUpdated?: Date | null;
}

export function LiveIndicator({
  isLive = true,
  lastUpdated,
}: LiveIndicatorProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.75,
        px: 1.5,
        py: 0.5,
        borderRadius: 3,
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(46, 125, 50, 0.15)'
            : 'rgba(46, 125, 50, 0.1)',
        border: '1px solid',
        borderColor: isLive ? 'success.main' : 'text.disabled',
      }}
    >
      <FiberManualRecord
        sx={{
          fontSize: 10,
          color: isLive ? 'success.main' : 'text.disabled',
          animation: isLive ? `${pulse} 2s ease-in-out infinite` : 'none',
          borderRadius: '50%',
          ...(isLive && {
            animation: `${pulse} 2s ease-in-out infinite, ${glow} 2s ease-in-out infinite`,
          }),
        }}
      />
      <Typography
        variant="caption"
        sx={{
          fontWeight: 600,
          letterSpacing: '0.05em',
          color: isLive ? 'success.main' : 'text.disabled',
          textTransform: 'uppercase',
          fontSize: '0.7rem',
        }}
      >
        {isLive ? 'LIVE' : 'OFFLINE'}
      </Typography>
      {lastUpdated && (
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            fontSize: '0.65rem',
            ml: 0.5,
          }}
        >
          •{' '}
          {lastUpdated.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Typography>
      )}
    </Box>
  );
}
```

**Step 2: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/common/LiveIndicator.tsx
git commit -m "feat: add LiveIndicator component with pulse animation"
```

---

### Task 5: Add Live Indicator to Header

**Files:**

- Modify: `src/components/core/Header.tsx:20-22,133-143`

**Step 1: Import LiveIndicator**

Add after the existing imports:

```tsx
import { LiveIndicator } from '../common/LiveIndicator';
```

**Step 2: Add LiveIndicator before the tagline**

Find this block (around line 133-143):

```tsx
<Typography
  sx={{
    color: 'rgba(255, 255, 255, 0.9)',
    letterSpacing: '0.1em',
    fontSize: { xs: '0.875rem', md: '1rem' },
    display: { xs: 'none', md: 'block' },
  }}
>
  KNOW FLOWS. CHASE RAPIDS. LIVE LARGE.
</Typography>
```

Replace with:

```tsx
<Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
  <LiveIndicator isLive={!isLoading} lastUpdated={null} />
  <Typography
    sx={{
      color: 'rgba(255, 255, 255, 0.9)',
      letterSpacing: '0.1em',
      fontSize: '1rem',
    }}
  >
    KNOW FLOWS. CHASE RAPIDS. LIVE LARGE.
  </Typography>
</Box>
```

**Step 3: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 4: Test visually**

Run: `npm run dev`
Verify: Header shows pulsing green "LIVE" indicator next to tagline

**Step 5: Commit**

```bash
git add src/components/core/Header.tsx
git commit -m "feat: add LiveIndicator to header showing data status"
```

---

## Phase 3: Liquid Fill Water Level Bar

### Task 6: Create LiquidFillBar Component

**Files:**

- Create: `src/components/common/LiquidFillBar.tsx`

**Step 1: Create the LiquidFillBar component**

```tsx
// src/components/common/LiquidFillBar.tsx
import { Box, Typography, keyframes, useTheme, Tooltip } from '@mui/material';
import { LevelStatus } from '../../types/stream';

const wave = keyframes`
  0% { transform: translateX(0) translateZ(0) scaleY(1); }
  50% { transform: translateX(-25%) translateZ(0) scaleY(0.8); }
  100% { transform: translateX(-50%) translateZ(0) scaleY(1); }
`;

const fillAnimation = keyframes`
  from { height: 0%; }
  to { height: var(--fill-height); }
`;

interface LiquidFillBarProps {
  currentValue: number;
  minValue: number;
  maxValue: number;
  status: LevelStatus;
  showLabel?: boolean;
  height?: number;
}

const STATUS_COLORS: Record<
  LevelStatus,
  { primary: string; secondary: string }
> = {
  [LevelStatus.Optimal]: { primary: '#2e7d32', secondary: '#4caf50' },
  [LevelStatus.Low]: { primary: '#ed6c02', secondary: '#ff9800' },
  [LevelStatus.High]: { primary: '#0288d1', secondary: '#03a9f4' },
  [LevelStatus.TooLow]: { primary: '#d32f2f', secondary: '#f44336' },
};

export function LiquidFillBar({
  currentValue,
  minValue,
  maxValue,
  status,
  showLabel = true,
  height = 60,
}: LiquidFillBarProps) {
  const theme = useTheme();
  const colors = STATUS_COLORS[status];

  // Calculate fill percentage (clamped between 0 and 100)
  const range = maxValue - minValue;
  const fillPercent = Math.min(
    100,
    Math.max(0, ((currentValue - minValue) / range) * 100)
  );

  const tooltipText = `${currentValue.toFixed(2)} ft (${fillPercent.toFixed(0)}% of range)`;

  return (
    <Tooltip title={tooltipText} arrow placement="top">
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: height,
          borderRadius: 2,
          overflow: 'hidden',
          background:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.05)'
              : 'rgba(0, 0, 0, 0.05)',
          border: '1px solid',
          borderColor:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.1)',
        }}
      >
        {/* Fill level */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: `${fillPercent}%`,
            background: `linear-gradient(180deg, ${colors.secondary} 0%, ${colors.primary} 100%)`,
            transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            '--fill-height': `${fillPercent}%`,
            animation: `${fillAnimation} 0.8s cubic-bezier(0.4, 0, 0.2, 1)`,
          }}
        >
          {/* Wave effect on top */}
          <Box
            sx={{
              position: 'absolute',
              top: -5,
              left: 0,
              width: '200%',
              height: 10,
              background: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 88.7'%3E%3Cpath d='M800 56.9c-155.5 0-204.9-50-405.5-49.9-200 0-250 49.9-394.5 49.9v31.8h800v-.2-31.6z' fill='${encodeURIComponent(colors.secondary)}'/%3E%3C/svg%3E")`,
              backgroundSize: '50% 100%',
              animation: `${wave} 3s linear infinite`,
              opacity: 0.6,
            }}
          />
        </Box>

        {/* Labels */}
        {showLabel && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 1,
              textAlign: 'center',
            }}
          >
            <Typography
              sx={{
                fontWeight: 700,
                fontSize: '0.9rem',
                color: fillPercent > 50 ? '#fff' : theme.palette.text.primary,
                textShadow:
                  fillPercent > 50 ? '0 1px 2px rgba(0,0,0,0.3)' : 'none',
              }}
            >
              {currentValue.toFixed(1)} ft
            </Typography>
          </Box>
        )}

        {/* Min/Max markers */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 4,
            left: 4,
            fontSize: '0.6rem',
            color: theme.palette.text.secondary,
            opacity: 0.7,
          }}
        >
          {minValue}
        </Box>
        <Box
          sx={{
            position: 'absolute',
            top: 4,
            right: 4,
            fontSize: '0.6rem',
            color: theme.palette.text.secondary,
            opacity: 0.7,
          }}
        >
          {maxValue}
        </Box>
      </Box>
    </Tooltip>
  );
}
```

**Step 2: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/common/LiquidFillBar.tsx
git commit -m "feat: add LiquidFillBar component with wave animation"
```

---

### Task 7: Add LiquidFillBar to StreamCard

**Files:**

- Modify: `src/components/streams/StreamCard.tsx:90-138`

**Step 1: Import LiquidFillBar**

Add after existing imports:

```tsx
import { LiquidFillBar } from '../common/LiquidFillBar';
```

**Step 2: Add LiquidFillBar in the reading display section**

Find the block that displays reading data (around lines 90-138). After the trend display and before the closing `</Box>`, add the LiquidFillBar.

Find this section:

```tsx
              <Typography variant="body2" color="text.secondary">
                Updated {relativeTime}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ mt: 1 }}
              >
                Optimal: {stream.targetLevels.tooLow}-{stream.targetLevels.high}{' '}
                ft
              </Typography>
```

Replace with:

```tsx
<Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
  Updated {relativeTime}
</Typography>;
{
  currentLevel?.status && (
    <LiquidFillBar
      currentValue={reading.value}
      minValue={stream.targetLevels.tooLow * 0.5}
      maxValue={stream.targetLevels.high * 1.5}
      status={currentLevel.status}
      height={40}
    />
  );
}
```

**Step 3: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 4: Test visually**

Run: `npm run dev`
Verify: Stream cards show animated liquid fill bar with wave effect

**Step 5: Commit**

```bash
git add src/components/streams/StreamCard.tsx
git commit -m "feat: add LiquidFillBar to StreamCard for visual water levels"
```

---

## Phase 4: Enhanced Card Effects

### Task 8: Add Glassmorphism to StreamCard

**Files:**

- Modify: `src/components/streams/StreamCard.tsx:43-54`

**Step 1: Import glassmorphism from waterTheme**

Add to imports:

```tsx
import { glassmorphism } from '../../theme/waterTheme';
```

**Step 2: Update Card sx prop to use glassmorphism**

Find the Card component's sx prop (around lines 43-54):

```tsx
      sx={{
        height: '100%',
        borderLeft: `4px solid ${statusColor}`,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        },
      }}
```

Replace with:

```tsx
      sx={{
        height: '100%',
        borderLeft: `4px solid ${statusColor}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        ...(theme.palette.mode === 'dark' ? glassmorphism.dark : glassmorphism.light),
        backdropFilter: 'blur(8px)',
        '&:hover': {
          transform: 'translateY(-4px) scale(1.01)',
          boxShadow: `0 12px 40px ${statusColor}30`,
          borderLeftWidth: '6px',
        },
      }}
```

**Step 3: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 4: Test visually**

Run: `npm run dev`
Verify: Cards have frosted glass effect and enhanced hover animation

**Step 5: Commit**

```bash
git add src/components/streams/StreamCard.tsx
git commit -m "feat: add glassmorphism effect to StreamCard"
```

---

### Task 9: Add Status Glow Effect to Cards

**Files:**

- Modify: `src/components/streams/StreamCard.tsx:43-54`

**Step 1: Import shadows from waterTheme**

Update the waterTheme import:

```tsx
import { glassmorphism, shadows } from '../../theme/waterTheme';
```

**Step 2: Add glow effect based on status**

Find the Card sx prop and add a glow effect. Update the sx to:

```tsx
      sx={{
        height: '100%',
        borderLeft: `4px solid ${statusColor}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        ...(theme.palette.mode === 'dark' ? glassmorphism.dark : glassmorphism.light),
        backdropFilter: 'blur(8px)',
        boxShadow: currentLevel?.status === LevelStatus.Optimal
          ? `0 0 20px ${statusColor}40`
          : 'none',
        '&:hover': {
          transform: 'translateY(-4px) scale(1.01)',
          boxShadow: `0 12px 40px ${statusColor}40`,
          borderLeftWidth: '6px',
        },
      }}
```

**Step 3: Import LevelStatus if not already imported**

Ensure LevelStatus is in the import:

```tsx
import { StreamData, LevelStatus, LevelTrend } from '../../types/stream';
```

**Step 4: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 5: Test visually**

Run: `npm run dev`
Verify: Optimal status cards have subtle green glow effect

**Step 6: Commit**

```bash
git add src/components/streams/StreamCard.tsx
git commit -m "feat: add status-based glow effect to optimal cards"
```

---

## Phase 5: Enhanced Table Interactions

### Task 10: Add Row Hover Glow to StreamTableRow

**Files:**

- Modify: `src/components/streams/StreamTableRow.tsx:59-71`

**Step 1: Enhance TableRow hover effect**

Find the TableRow sx prop (around lines 59-71):

```tsx
      sx={{
        cursor: 'pointer',
        '&:hover': {
          backgroundColor:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.08)'
              : 'rgba(0, 0, 0, 0.04)',
        },
      }}
```

Replace with:

```tsx
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          backgroundColor:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.08)'
              : 'rgba(0, 0, 0, 0.04)',
          transform: 'scale(1.005)',
          boxShadow: theme.palette.mode === 'dark'
            ? '0 4px 20px rgba(0, 0, 0, 0.3)'
            : '0 4px 20px rgba(0, 0, 0, 0.1)',
        },
        '&:active': {
          transform: 'scale(0.995)',
        },
      }}
```

**Step 2: Verify compilation**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamTableRow.tsx
git commit -m "feat: add enhanced hover effect to table rows"
```

---

## Phase 6: Final Polish

### Task 11: Run Full Build and Lint

**Step 1: Run linting**

Run: `npm run lint`
Expected: No errors

**Step 2: Run full build**

Run: `npm run build`
Expected: Build completes successfully

**Step 3: Run preview to test production build**

Run: `npm run preview`
Verify: All UI changes work correctly in production build

---

### Task 12: Final Commit and Push

**Step 1: Check git status**

Run: `git status`
Verify: All changes are committed

**Step 2: Push to remote**

Run: `git push`
Expected: Push succeeds

---

## Summary of Changes

| Component      | Enhancement                            |
| -------------- | -------------------------------------- |
| StreamSkeleton | Shimmer animation skeleton loader      |
| LiveIndicator  | Pulsing "LIVE" badge with glow         |
| LiquidFillBar  | Animated water fill with wave effect   |
| StreamCard     | Glassmorphism + status glow + fill bar |
| StreamTableRow | Enhanced hover with lift and shadow    |
| Header         | Live data indicator integration        |

## Files Created

- `src/components/common/StreamSkeleton.tsx`
- `src/components/common/LiveIndicator.tsx`
- `src/components/common/LiquidFillBar.tsx`

## Files Modified

- `src/components/streams/StreamCard.tsx`
- `src/components/streams/StreamTableRow.tsx`
- `src/components/core/Header.tsx`
