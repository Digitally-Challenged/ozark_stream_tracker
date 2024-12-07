# .bolt/config.json

```json
{
  "template": "bolt-vite-react-ts"
}

```

# .bolt/prompt

```
For all designs I ask you to make, have them be beautiful, not cookie cutter. Make webpages that are fully featured and worthy for production.

By default, this template supports JSX syntax with Tailwind CSS classes, React hooks, and Lucide React for icons. Do not install other packages for UI themes, icons, etc unless absolutely necessary or I request them.

Use icons from lucide-react for logos.

Use stock photos from unsplash where appropriate, only valid URLs you know exist. Do not download the images, only link to them in image tags.


```

# .gitignore

```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

```

# eslint.config.js

```js
import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  }
);

```

# index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React + TS</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

```

# package.json

```json
{
  "name": "mountain-stream-tracker",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.16.8",
    "@mui/material": "^5.15.10",
    "date-fns": "^3.3.1",
    "lucide-react": "^0.344.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-error-boundary": "^4.0.12",
    "react-router-dom": "^6.22.1"
  },
  "devDependencies": {
    "@eslint/js": "^9.9.1",
    "@tailwindcss/forms": "^0.5.9",
    "@tailwindcss/typography": "^0.5.15",
    "@types/react": "^18.3.5",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.18",
    "eslint": "^9.9.1",
    "eslint-plugin-react-hooks": "^5.1.0-rc.0",
    "eslint-plugin-react-refresh": "^0.4.11",
    "globals": "^15.9.0",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.5.3",
    "typescript-eslint": "^8.3.0",
    "vite": "^5.4.2"
  }
}

```

# postcss.config.js

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};

```

# README.md

```md
# ozark_stream_tracker

[Edit in StackBlitz next generation editor ⚡️](https://stackblitz.com/~/github.com/Digitally-Challenged/ozark_stream_tracker)
```

# src/App.tsx

```tsx
import React, { useState } from 'react';
import { Box, Container, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { StreamTable } from './components/streams/StreamTable';
import { StreamDetail } from './components/streams/StreamDetail';
import { DashboardHeader } from './components/dashboard/DashboardHeader';
import { DashboardSidebar } from './components/dashboard/DashboardSidebar';
import { ThemeProvider } from './context/ThemeContext';
import { streams } from './data/streamData';
import { StreamData } from './types/stream';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function ErrorFallback({ error }: { error: Error }) {
  return (
    <Box sx={{ p: 4 }}>
      <h2>Something went wrong:</h2>
      <pre>{error.message}</pre>
    </Box>
  );
}

function DashboardContent() {
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container 
        component="main" 
        sx={{ 
          mt: 4, 
          mb: 4, 
          flex: 1,
          maxWidth: { xl: '1400px' } 
        }}
      >
        <DashboardHeader />
        <StreamTable
          streams={streams}
          onStreamClick={(stream) => setSelectedStream(stream)}
        />
      </Container>
      <StreamDetail
        stream={selectedStream}
        open={selectedStream !== null}
        onClose={() => setSelectedStream(null)}
      />
    </Box>
  );
}

function App() {
  const [filterOpen, setFilterOpen] = useState(false);

  return (
    <ThemeProvider>
      <CssBaseline />
      <BrowserRouter>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            bgcolor: (theme) => theme.palette.mode === 'dark' ? '#121212' : '#f5f5f5',
          }}
        >
          <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Header 
              onFilterClick={() => setFilterOpen(!filterOpen)} 
              filterOpen={filterOpen}
            />
            <Box sx={{ display: 'flex', flex: 1 }}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardContent />} />
              </Routes>
            </Box>
            <DashboardSidebar
              open={filterOpen}
              onClose={() => setFilterOpen(false)}
            />
            <Footer />
          </ErrorBoundary>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;

```

# src/components/core/Footer.tsx

```tsx
export function Footer() {
  return (
    <footer className="py-6 px-4 mt-auto bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-2xl mx-auto">
        <p className="text-sm text-center text-gray-600 dark:text-gray-400">
          © {' '}
          <a
            href="#"
            className="text-inherit hover:text-primary-main hover:underline transition-colors"
          >
            Mountain Stream Tracker
          </a>{' '}
          {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
```

# src/components/core/Header.tsx

```tsx
import { AppBar, Toolbar, Typography, IconButton, useTheme, Box } from '@mui/material';
import { Moon, Sun } from 'lucide-react';
import { Kayaking, FilterList } from '@mui/icons-material';
import { useTheme as useColorMode } from '../../context/ThemeContext';

interface HeaderProps {
  onFilterClick: () => void;
  filterOpen: boolean;
}

export function Header({ onFilterClick, filterOpen }: HeaderProps) {
  const { mode, toggleColorMode } = useColorMode();
  const theme = useTheme();

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{
        backgroundColor: 'rgb(17, 24, 39)',
        borderBottom: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          gap: 2
        }}>
          <Box sx={{ 
            color: 'white',
            display: 'flex',
            alignItems: 'center'
          }}>
            <Kayaking sx={{ fontSize: 32 }} />
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'white',
              letterSpacing: '0.2em',
              fontWeight: 300
            }}
          >
            OZARK CREEK FLOW ZONE
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.9)',
              letterSpacing: '0.1em',
              fontSize: { xs: '0.875rem', md: '1rem' },
              display: { xs: 'none', md: 'block' }
            }}
          >
            KNOW FLOWS. CHASE RAPIDS. LIVE LARGE.
          </Typography>
          
          <IconButton 
            onClick={onFilterClick}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              transform: filterOpen ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.3s ease'
            }}
          >
            <FilterList />
          </IconButton>
          
          <IconButton 
            onClick={toggleColorMode}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            {mode === 'dark' ? (
              <Sun size={20} />
            ) : (
              <Moon size={20} />
            )}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
```

# src/components/dashboard/DashboardHeader.tsx

```tsx
import { Box, Typography, Paper, Grid, useTheme, Tooltip } from '@mui/material';
import { WaterDrop, Waves, Terrain, AccessTime } from '@mui/icons-material';
import { keyframes } from '@mui/system';

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulseIcon = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
`;

export function DashboardHeader() {
  const theme = useTheme();

  const statsData = [
    {
      label: 'Total Runs',
      value: '93',
      icon: WaterDrop,
      color: theme.palette.primary.main,
      tooltip: 'Total number of whitewater runs'
    },
    {
      label: 'Beginner Runs',
      value: '87',
      icon: Waves,
      color: theme.palette.success.main,
      tooltip: 'Class I-II runs'
    },
    {
      label: 'Advanced Runs',
      value: '40',
      icon: Terrain,
      color: theme.palette.warning.main,
      tooltip: 'Class IV-V runs'
    },
    {
      label: 'Last Updated',
      value: '3:25:16 PM',
      icon: AccessTime,
      color: theme.palette.info.main,
      tooltip: 'Most recent gauge reading update'
    }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={3}>
        {statsData.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Tooltip title={stat.tooltip} arrow>
              <Paper
                sx={{
                  p: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  bgcolor: theme.palette.mode === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(0, 0, 0, 0.02)',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.3s ease-in-out',
                  animation: `${fadeInUp} 0.5s ease-out ${index * 0.1}s`,
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    bgcolor: theme.palette.mode === 'dark'
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(0, 0, 0, 0.04)',
                    boxShadow: theme.shadows[8],
                  },
                }}
                elevation={0}
              >
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: theme.palette.mode === 'dark'
                      ? `${stat.color}15`
                      : `${stat.color}15`,
                    color: stat.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    '&:hover': {
                      animation: `${pulseIcon} 1s ease-in-out infinite`
                    }
                  }}
                >
                  <stat.icon sx={{ fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography 
                    variant="body2"
                    sx={{ 
                      color: theme.palette.text.secondary,
                      fontWeight: 500
                    }}
                  >
                    {stat.label}
                  </Typography>
                  <Typography 
                    variant="h5" 
                    sx={{ 
                      mt: 0.5,
                      color: theme.palette.text.primary,
                      fontWeight: 600
                    }}
                  >
                    {stat.value}
                  </Typography>
                </Box>
              </Paper>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
```

# src/components/dashboard/DashboardLayout.tsx

```tsx
import { useState } from 'react';
import { Box, IconButton, useTheme } from '@mui/material';
import { FilterList } from '@mui/icons-material';
import { DashboardSidebar } from './DashboardSidebar';
import { DashboardHeader } from './DashboardHeader';
import { Outlet } from 'react-router-dom';

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <DashboardSidebar
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />
      
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          minHeight: '100vh',
          backgroundColor: theme.palette.mode === 'dark' 
            ? 'rgb(17, 24, 39)' 
            : 'rgb(249, 250, 251)',
        }}
      >
        {/* Mobile filter button */}
        <Box sx={{ 
          display: { xs: 'block', md: 'none' }, 
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 1000
        }}>
          <IconButton 
            onClick={handleDrawerToggle}
            sx={{ 
              bgcolor: theme.palette.primary.main,
              color: 'white',
              '&:hover': {
                bgcolor: theme.palette.primary.dark,
              },
              width: 56,
              height: 56,
              boxShadow: theme.shadows[4],
            }}
          >
            <FilterList />
          </IconButton>
        </Box>

        <DashboardHeader />
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}

```

# src/components/dashboard/DashboardSidebar.tsx

```tsx
import { 
  Box, 
  Drawer, 
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider
} from '@mui/material';
import { Close } from '@mui/icons-material';

interface DashboardSidebarProps {
  open: boolean;
  onClose: () => void;
  width?: number;
}

export function DashboardSidebar({ 
  open = false, 
  onClose, 
  width = 320 
}: DashboardSidebarProps) {
  const menuItems = [
    { label: 'Learn More', href: '/learn' },
    { label: 'Contact', href: '/contact' },
    { label: 'Trail Finder', href: '/trails' },
    { label: '❤️ the app?', href: '/feedback' },
    { label: 'Buy us a coffee!', href: '/support' },
    { label: 'Venmo', href: '/venmo' },
    { label: 'PayPal', href: '/paypal' }
  ];

  const content = (
    <Box
      sx={{
        height: '100%',
        backgroundColor: 'rgb(17, 24, 39)',
        color: 'white',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'flex-end',
        p: 2
      }}>
        <IconButton 
          onClick={onClose} 
          sx={{ color: 'white' }}
        >
          <Close />
        </IconButton>
      </Box>

      <List sx={{ flex: 1, pt: 0 }}>
        {menuItems.map((item, index) => (
          <Box key={item.label}>
            <ListItem disablePadding>
              <ListItemButton
                sx={{
                  py: 2,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    sx: {
                      color: 'white',
                      fontSize: '1rem',
                      fontWeight: 400
                    }
                  }}
                />
              </ListItemButton>
            </ListItem>
            {index < menuItems.length - 1 && (
              <Divider 
                sx={{ 
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  mx: 2
                }} 
              />
            )}
          </Box>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      variant="temporary"
      elevation={4}
      sx={{
        '& .MuiDrawer-paper': { 
          width,
          boxSizing: 'border-box',
          backgroundColor: 'rgb(17, 24, 39)',
          border: 'none'
        }
      }}
    >
      {content}
    </Drawer>
  );
}

```

# src/components/streams/StreamDetail.tsx

```tsx
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Box,
  useTheme,
} from '@mui/material';
import { Droplet, Thermometer, Clock, Activity } from 'lucide-react';
import { StreamData } from '../../types/stream';
import { format, isValid } from 'date-fns';

interface StreamDetailProps {
  stream: StreamData | null;
  open: boolean;
  onClose: () => void;
}

export function StreamDetail({ stream, open, onClose }: StreamDetailProps) {
  const theme = useTheme();
  
  if (!stream) return null;

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not available';
    const date = new Date(dateString);
    return isValid(date) ? format(date, 'PPpp') : 'Invalid date';
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: theme.palette.background.paper,
          backgroundImage: 'none',
        }
      }}
    >
      <DialogTitle sx={{ 
        borderBottom: `1px solid ${theme.palette.divider}`,
        color: theme.palette.text.primary,
      }}>
        {stream.name}
      </DialogTitle>
      
      <DialogContent sx={{ py: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Droplet size={20} color={theme.palette.primary.main} />
              <Typography color="text.primary">
                Flow Rate: {stream.currentFlow ? `${stream.currentFlow} cfs` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Thermometer size={20} color={theme.palette.primary.main} />
              <Typography color="text.primary">
                Temperature: {stream.temperature ? `${stream.temperature}°F` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Activity size={20} color={theme.palette.primary.main} />
              <Typography color="text.primary">
                Status: {stream.status || 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Clock size={20} color={theme.palette.primary.main} />
              <Typography color="text.primary">
                Last Updated: {formatDate(stream.lastUpdated)}
              </Typography>
            </Box>
          </Grid>

          {stream.waterQuality && (
            <Grid item xs={12}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  color: theme.palette.text.primary,
                  fontWeight: 500,
                  mt: 2 
                }}
              >
                Water Quality
              </Typography>
              <Box sx={{ pl: 1 }}>
                <Typography color="text.primary" paragraph>
                  pH: {stream.waterQuality.ph || 'Not available'}
                </Typography>
                <Typography color="text.primary" paragraph>
                  Turbidity: {stream.waterQuality.turbidity ? `${stream.waterQuality.turbidity} NTU` : 'Not available'}
                </Typography>
                <Typography color="text.primary">
                  Dissolved Oxygen: {stream.waterQuality.dissolvedOxygen ? `${stream.waterQuality.dissolvedOxygen} mg/L` : 'Not available'}
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions sx={{ 
        borderTop: `1px solid ${theme.palette.divider}`,
        px: 3,
        py: 2,
      }}>
        <Button 
          onClick={onClose}
          variant="contained"
          sx={{
            bgcolor: theme.palette.primary.main,
            '&:hover': {
              bgcolor: theme.palette.primary.dark,
            },
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
```

# src/components/streams/StreamInfoTooltip.tsx

```tsx
import { Box, Typography, useTheme } from '@mui/material';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import { 
  getSizeDefinition, 
  getCorrelationDefinition, 
  getLevelDefinition,
  getRatingDefinition,
  sizeDefinitions,
  correlationDefinitions 
} from '../../types/streamDefinitions';
import { LevelTrend } from '../../types/stream';

interface InfoTooltipProps {
  type: 'size' | 'correlation' | 'level' | 'rating';
  value: string;
  trend?: LevelTrend;
}

export default function InfoTooltip({ type, value, trend }: InfoTooltipProps) {
  const theme = useTheme();

  const renderTrendIcon = () => {
    if (!trend) return null;

    const iconProps = { 
      size: 16,
      strokeWidth: 2.5
    };

    switch (trend) {
      case LevelTrend.Rising:
        return <ArrowUp {...iconProps} color={theme.palette.success.main} />;
      case LevelTrend.Falling:
        return <ArrowDown {...iconProps} color={theme.palette.error.main} />;
      case LevelTrend.Holding:
        return <Minus {...iconProps} color={theme.palette.text.secondary} />;
      default:
        return null;
    }
  };

  const renderLevelContent = () => {
    const levelKey = value === 'X' ? 'tooLow' : 
                    value === 'L' ? 'low' : 
                    value === 'O' ? 'optimal' : 
                    value === 'H' ? 'high' : null;
                    
    if (!levelKey) return null;
    const info = getLevelDefinition(levelKey);

    return (
      <Box sx={{ p: 1 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            mb: 1 
          }}
        >
          <Typography 
            variant="subtitle1" 
            sx={{ 
              fontWeight: 600,
              color: theme.palette.text.primary 
            }}
          >
            {info.name}
          </Typography>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: info.color
            }}
          />
          {renderTrendIcon()}
        </Box>
        <Typography 
          variant="body2"
          sx={{ color: theme.palette.text.secondary }}
        >
          {info.description}
        </Typography>
        {trend && trend !== LevelTrend.None && (
          <Typography 
            variant="body2" 
            sx={{ 
              mt: 1,
              color: trend === LevelTrend.Rising ? theme.palette.success.main :
                     trend === LevelTrend.Falling ? theme.palette.error.main :
                     theme.palette.text.secondary
            }}
          >
            Level is {trend.toLowerCase()}
          </Typography>
        )}
      </Box>
    );
  };

  const renderSizeContent = () => {
    const info = getSizeDefinition(value as keyof typeof sizeDefinitions);
    return (
      <Box sx={{ p: 1 }}>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1 
          }}
        >
          {info.name}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Typography 
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Width: {info.width}
          </Typography>
          <Typography 
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Watershed: {info.watershed}
          </Typography>
          <Typography 
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Rain Rate: {info.rainRate}
          </Typography>
          <Typography 
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Window: {info.window}
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              mt: 1,
              color: theme.palette.text.primary 
            }}
          >
            {info.description}
          </Typography>
        </Box>
      </Box>
    );
  };

  const renderCorrelationContent = () => {
    const info = getCorrelationDefinition(value as keyof typeof correlationDefinitions);
    return (
      <Box sx={{ p: 1 }}>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1 
          }}
        >
          {info.name}
        </Typography>
        <Typography 
          variant="body2"
          sx={{ color: theme.palette.text.secondary }}
        >
          {info.description}
        </Typography>
      </Box>
    );
  };

  const renderRatingContent = () => {
    const info = getRatingDefinition(value);
    return (
      <Box sx={{ p: 1, maxWidth: 300 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            mb: 1 
          }}
        >
          <Typography 
            variant="subtitle1" 
            sx={{ 
              fontWeight: 600,
              color: theme.palette.text.primary 
            }}
          >
            {info.name}
          </Typography>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: info.color
            }}
          />
        </Box>
        <Typography 
          variant="body2"
          sx={{ 
            color: theme.palette.text.secondary,
            lineHeight: 1.5 
          }}
        >
          {info.description}
        </Typography>
      </Box>
    );
  };

  switch (type) {
    case 'level':
      return renderLevelContent();
    case 'size':
      return renderSizeContent();
    case 'correlation':
      return renderCorrelationContent();
    case 'rating':
      return renderRatingContent();
    default:
      return null;
  }
}
```

# src/components/streams/StreamTable.tsx

```tsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableContainer,
  Paper,
  Box,
  TextField,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { StreamData } from '../../types/stream';
import { StreamTableHeader } from './StreamTableHeader';
import { StreamTableRow } from './StreamTableRow';
import { SortDirection, SortField } from '../../types/table';
import { sortStreams } from '../../utils/sorting';

interface StreamTableProps {
  streams: StreamData[];
  onStreamClick: (stream: StreamData) => void;
}

export function StreamTable({ streams, onStreamClick }: StreamTableProps) {
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (field: SortField) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const filteredStreams = streams.filter((stream) => {
    const searchLower = searchTerm.toLowerCase();
    return stream.name.toLowerCase().includes(searchLower) ||
           stream.gauge.name.toLowerCase().includes(searchLower);
  });

  const sortedStreams = sortStreams(filteredStreams, sortField, sortDirection);

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        mb: 2,
        maxWidth: 400,
        position: 'relative'
      }}>
        <Search sx={{ 
          position: 'absolute',
          left: 8,
          color: 'text.secondary'
        }} />
        <TextField
          placeholder="Search streams..."
          variant="outlined"
          size="small"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{
            '& .MuiOutlinedInput-root': {
              pl: 4.5,
              '& fieldset': {
                borderColor: 'divider',
              },
            },
          }}
        />
      </Box>
      <TableContainer 
        component={Paper} 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper',
          '& .MuiTableCell-root': {
            py: 1.5,
            px: 2,
            fontSize: '0.875rem',
          }
        }}
      >
        <Table size="small">
          <StreamTableHeader
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />
          <TableBody>
            {sortedStreams.map((stream) => (
              <StreamTableRow
                key={`${stream.name}-${stream.gauge.id}`}
                stream={stream}
                onClick={onStreamClick}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
```

# src/components/streams/StreamTableHeader.tsx

```tsx
import React from 'react';
import { TableHead, TableRow, TableCell, TableSortLabel } from '@mui/material';
import { SortDirection, SortField } from '../../types/table';

interface StreamTableHeaderProps {
  sortField: SortField;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
}

export function StreamTableHeader({ sortField, sortDirection, onSort }: StreamTableHeaderProps) {
  const headers: { field: SortField; label: string }[] = [
    { field: 'name', label: 'Stream Name' },
    { field: 'rating', label: 'Rating' },
    { field: 'size', label: 'Size' },
    { field: 'gauge', label: 'Reference Gauge' },
    { field: 'reading', label: 'Gauge Reading' },
    { field: 'quality', label: 'Quality' },
    { field: 'level', label: 'Current Level' },
    { field: 'trend', label: 'Trend' }
  ];

  return (
    <TableHead>
      <TableRow>
        {headers.map(({ field, label }) => (
          <TableCell key={field}>
            <TableSortLabel
              active={sortField === field}
              direction={sortField === field ? sortDirection : 'asc'}
              onClick={() => onSort(field)}
            >
              {label}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}
```

# src/components/streams/StreamTableRow.tsx

```tsx
import { TableRow, TableCell, Tooltip, useTheme } from '@mui/material';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';
import { StreamData, LevelTrend } from '../../types/stream';
import { useStreamGauge } from '../../hooks/useStreamGauge';
import InfoTooltip from './StreamInfoTooltip';

interface StreamTableRowProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

export function StreamTableRow({ stream, onClick }: StreamTableRowProps) {
  const { currentLevel, reading, loading, error } = useStreamGauge(stream);
  const theme = useTheme();

  const getLevelColor = (status: string | undefined) => {
    if (!status) return undefined;
    
    const alpha = theme.palette.mode === 'dark' ? '0.3' : '0.2';
    switch (status) {
      case 'X': return theme.palette.mode === 'dark'
        ? `rgba(211, 47, 47, ${alpha})`  // Dark mode red - Too Low
        : `rgba(211, 47, 47, ${alpha})`; // Light mode red
      case 'L': return theme.palette.mode === 'dark'
        ? `rgba(237, 108, 2, ${alpha})`  // Dark mode orange - Low
        : `rgba(237, 108, 2, ${alpha})`; // Light mode orange
      case 'O': return theme.palette.mode === 'dark'
        ? `rgba(46, 125, 50, ${alpha})`  // Dark mode green - Optimal
        : `rgba(46, 125, 50, ${alpha})`; // Light mode green
      case 'H': return theme.palette.mode === 'dark'
        ? `rgba(2, 136, 209, ${alpha})`  // Dark mode blue - High/Flood
        : `rgba(2, 136, 209, ${alpha})`; // Light mode blue
      default: return undefined;
    }
  };

  const renderTrendIcon = () => {
    if (!currentLevel?.trend || currentLevel.trend === LevelTrend.None) return null;

    const iconProps = { 
      size: 16,
      strokeWidth: 2.5,
      className: 'ml-2'
    };

    switch (currentLevel.trend) {
      case LevelTrend.Rising:
        return <ArrowUp {...iconProps} color={theme.palette.success.main} />;
      case LevelTrend.Falling:
        return <ArrowDown {...iconProps} color={theme.palette.error.main} />;
      case LevelTrend.Holding:
        return <Minus {...iconProps} color={theme.palette.text.secondary} />;
      default:
        return null;
    }
  };

  return (
    <TableRow 
      hover
      onClick={() => onClick(stream)}
      sx={{ 
        cursor: 'pointer',
        '&:hover': {
          backgroundColor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.08)' 
            : 'rgba(0, 0, 0, 0.04)',
        },
      }}
    >
      <TableCell>{stream.name}</TableCell>
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="rating" value={stream.rating} />}
          placement="right"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.rating}</span>
        </Tooltip>
      </TableCell>
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="size" value={stream.size} />}
          placement="right"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.size}</span>
        </Tooltip>
      </TableCell>
      <TableCell>
        <Tooltip title="View USGS Gauge Page">
          <a
            href={stream.gauge.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-blue-500 hover:underline"
          >
            {stream.gauge.name}
          </a>
        </Tooltip>
      </TableCell>
      <TableCell>
        {reading && !loading && !error ? (
          <Tooltip title={`Last updated: ${new Date(reading.timestamp).toLocaleString()}`}>
            <span>{reading.value.toFixed(2)} ft</span>
          </Tooltip>
        ) : loading ? (
          'Loading...'
        ) : error ? (
          <Tooltip title={error.message}>
            <span>Error</span>
          </Tooltip>
        ) : (
          'N/A'
        )}
      </TableCell>
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="correlation" value={stream.quality} />}
          placement="left"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.quality}</span>
        </Tooltip>
      </TableCell>
      <TableCell 
        sx={{ 
          bgcolor: getLevelColor(currentLevel?.status),
          transition: 'background-color 0.2s ease',
        }}
      >
        <Tooltip
          title={<InfoTooltip 
            type="level" 
            value={currentLevel?.status || 'N/A'} 
            trend={currentLevel?.trend}
          />}
          placement="left"
          arrow
        >
          <span className="flex items-center">
            {loading ? 'Loading...' : error ? 'Error' : (
              <>
                {currentLevel?.status || 'N/A'}
                {renderTrendIcon()}
              </>
            )}
          </span>
        </Tooltip>
      </TableCell>
    </TableRow>
  );
}
```

# src/context/ThemeContext.tsx

```tsx
import React, { createContext, useContext, useState, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import { PaletteMode } from '@mui/material';

interface ThemeContextType {
  mode: PaletteMode;
  toggleColorMode: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  mode: 'light',
  toggleColorMode: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<PaletteMode>('light');

  const colorMode = useMemo(
    () => ({
      mode,
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [mode]
  );

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: '#2196f3',
          },
          secondary: {
            main: '#4caf50',
          },
          background: {
            default: mode === 'dark' ? '#121212' : '#f5f5f5',
            paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          },
          text: {
            primary: mode === 'dark' ? '#ffffff' : '#000000',
            secondary: mode === 'dark' ? '#b0b0b0' : '#666666',
          },
        },
        components: {
          MuiTableCell: {
            styleOverrides: {
              root: {
                borderColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
              },
              head: {
                fontWeight: 600,
                backgroundColor: mode === 'dark' ? '#272727' : '#f5f5f5',
              },
            },
          },
          MuiTableRow: {
            styleOverrides: {
              root: {
                '&:hover': {
                  backgroundColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
                },
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
          MuiTooltip: {
            styleOverrides: {
              tooltip: {
                backgroundColor: mode === 'dark' ? '#424242' : '#ffffff',
                color: mode === 'dark' ? '#ffffff' : '#000000',
                border: `1px solid ${mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)'}`,
                boxShadow: mode === 'dark' 
                  ? '0 4px 6px rgba(0, 0, 0, 0.3)' 
                  : '0 4px 6px rgba(0, 0, 0, 0.1)',
              },
            },
          },
        },
      }),
    [mode]
  );

  return (
    <ThemeContext.Provider value={colorMode}>
      <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>
    </ThemeContext.Provider>
  );
}
```

# src/data/streamData.ts

```ts
import { StreamData } from '../types/stream';

export const streams: StreamData[] = [
   {
    name: "Adkins Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.5,
      high: 11.0
    }
  },
  {
    name: "Archey Cr.",
    rating: "II+",
    size: "M",
    gauge: {
      name: "Big Piney Cr at Hwy 164 nr Dover",
      id: "07257006",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257006"
    },
    quality: "C",
    targetLevels: {
      tooLow: 4.0,
      optimal: 5.5,
      high: 8.0
    }
  },
  {
    name: "Baker Cr.",
    rating: "II-IV",
    size: "S",
    gauge: {
      name: "Cossatot R. at Vandervoort",
      id: "07340300",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07340300"
    },
    quality: "B",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.0,
      high: 8.0
    }
  },
  {
    name: "Bear Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Beech Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.5,
      optimal: 8.5,
      high: 10.0
    }
  },
  {
    name: "Ben Doodle Cr.",
    rating: "IV-V",
    size: "XS",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 14.0,
      optimal: 18.0,
      high: 24.0
    }
  },
  {
    name: "Big Devils Fork Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Big Piney Cr (abv Longpool)",
    rating: "II+",
    size: "L",
    gauge: {
      name: "Big Piney Cr at Hwy 164 nr Dover",
      id: "07257006",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257006"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.0,
      optimal: 3.0,
      high: 5.0
    }
  },
  {
    name: "Big Piney Cr (blw Longpool)",
    rating: "I-II",
    size: "L",
    gauge: {
      name: "Big Piney Cr at Hwy 164 nr Dover",
      id: "07257006",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257006"
    },
    quality: "A",
    targetLevels: {
      tooLow: 1.2,
      optimal: 2.0,
      high: 5.0
    }
  },
  {
    name: "Blackburn Cr.",
    rating: "II-III",
    size: "S",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "B",
    targetLevels: {
      tooLow: 6.5,
      optimal: 7.8,
      high: 10.0
    }
  },
  {
    name: "Bobtail Cr.",
    rating: "III-IV+",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 4.5,
      optimal: 6.5,
      high: 8.0
    }
  },
  {
    name: "Boss Hollow",
    rating: "IV-V",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Boulder Cr.",
    rating: "IV-V+ (P)",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.5,
      high: 10.0
    }
  },
  {
    name: "Buffalo R. (below Ponca)",
    rating: "I-II",
    size: "L",
    gauge: {
      name: "Buffalo R. at Ponca",
      id: "07055660",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055660"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.0,
      optimal: 3.7,
      high: 6.3
    }
  },
  {
    name: "Buffalo R. (Boxley Valley)",
    rating: "II",
    size: "L",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.7,
      optimal: 4.2,
      high: 5.8
    }
  },
  {
    name: "Caddo R.",
    rating: "I-II",
    size: "L",
    gauge: {
      name: "Caddo R. nr Caddo Gap",
      id: "07359610",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07359610"
    },
    quality: "A",
    targetLevels: {
      tooLow: 5.3,
      optimal: 5.75,
      high: 7.25
    }
  },
  {
    name: "Cadron Cr.",
    rating: "I-II+",
    size: "L",
    gauge: {
      name: "Cadron Cr. nr Guy",
      id: "07261000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07261000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 1.5,
      optimal: 2.0,
      high: 6.0
    }
  },
  {
    name: "Camp Cr.",
    rating: "IV+",
    size: "S",
    gauge: {
      name: "Little Missouri R. nr Langley",
      id: "07360200",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07360200"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.5,
      high: 9.0
    }
  },
  {
    name: "Cedar Cr.",
    rating: "II+",
    size: "S",
    gauge: {
      name: "Frog Bayou at Rudy",
      id: "07251500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07251500"
    },
    quality: "B",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.0,
      high: 7.5
    }
  },
  {
    name: "Clear Cr.",
    rating: "II-III",
    size: "S",
    gauge: {
      name: "Frog Bayou at Rudy",
      id: "07251500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07251500"
    },
    quality: "B",
    targetLevels: {
      tooLow: 4.5,
      optimal: 5.5,
      high: 7.5
    }
  },
  {
    name: "Cossatot R.",
    rating: "II-IV",
    size: "L",
    gauge: {
      name: "Cossatot R. at Vandervoort",
      id: "07340300",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07340300"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.0,
      optimal: 3.4,
      high: 5.5
    }
  },
  {
    name: "Crooked Cr.",
    rating: "III-IV (V)",
    size: "VS",
    gauge: {
      name: "Little Missouri R. nr Langley",
      id: "07360200",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07360200"
    },
    quality: "B",
    targetLevels: {
      tooLow: 7.5,
      optimal: 9.5,
      high: 11.0
    }
  },
 {
    name: "Dragover (Ouachita R.)",
    rating: "I-II",
    size: "L",
    gauge: {
      name: "USGS: Ouachita River nr Mount Ida",
      id: "07356000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07356000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.75,
      optimal: 3.5,
      high: 6.5
    }
  },
  {
    name: "E. Fk. White R.",
    rating: "II",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "D",
    targetLevels: {
      tooLow: 4.0,
      optimal: 5.0,
      high: 7.0
    }
  },
  {
    name: "EFLB",
    rating: "III-IV (V)",
    size: "S",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "C",
    targetLevels: {
      tooLow: 5.8,
      optimal: 6.5,
      high: 9.0
    }
  },
  {
    name: "Ellis Cr.",
    rating: "III-IV",
    size: "XS",
    gauge: {
      name: "Baron Fork at Dutch Mills",
      id: "07196900",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07196900"
    },
    quality: "C",
    targetLevels: {
      tooLow: 5.5,
      optimal: 6.5,
      high: 8.0
    }
  },
  {
    name: "Fall Cr.",
    rating: "II-IV",
    size: "S",
    gauge: {
      name: "Baron Fork at Dutch Mills",
      id: "07196900",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07196900"
    },
    quality: "C",
    targetLevels: {
      tooLow: 3.75,
      optimal: 5.0,
      high: 6.0
    }
  },
  {
    name: "Falling Water Cr.",
    rating: "III",
    size: "S",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "B",
    targetLevels: {
      tooLow: 4.0,
      optimal: 5.0,
      high: 6.5
    }
  },
  {
    name: "Falls Br.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Fern Gulley",
    rating: "IV-V",
    size: "XS",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 11.0,
      optimal: 12.0,
      high: 15.0
    }
  },
  {
    name: "Fisher's Ford",
    rating: "PLAY",
    size: "A",
    gauge: {
      name: "Illinois R. nr Siloam Springs",
      id: "07195430",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07195430"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.1,
      optimal: 3.7,
      high: 5.0
    }
  },
  {
    name: "Frog Bayou",
    rating: "II",
    size: "L",
    gauge: {
      name: "Frog Bayou at Rudy",
      id: "07251500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07251500"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.0,
      optimal: 2.7,
      high: 4.3
    }
  },
  {
    name: "Gutter Rock Cr.",
    rating: "III+",
    size: "VS",
    gauge: {
      name: "Dutch Cr. at Waltreak",
      id: "07260000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07260000"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 7.2,
      optimal: 8.5,
      high: 10.0
    }
  },
  {
    name: "Hailstone Cr.",
    rating: "II-III+",
    size: "S",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.8,
      optimal: 5.3,
      high: 6.5
    }
  },
  {
    name: "Hart Cr.",
    rating: "III-IV (V)",
    size: "VS",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 11.0,
      optimal: 14.0,
      high: 22.0
    }
  },
  {
    name: "Haw Cr.",
    rating: "II+-III",
    size: "VS",
    gauge: {
      name: "Big Piney Cr at Hwy 164 nr Dover",
      id: "07257006",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257006"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 5.5,
      optimal: 7.0,
      high: 10.0
    }
  },
  {
    name: "Hurricane Cr. (Franklin)",
    rating: "II+",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 10.0
    }
  },
  {
    name: "Hurricane Cr. (Newton)",
    rating: "II+-III",
    size: "S",
    gauge: {
      name: "Big Piney Cr at Hwy 164 nr Dover",
      id: "07257006",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257006"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.0,
      high: 8.5
    }
  },
  {
    name: "Kings River (lower)",
    rating: "A",
    size: "L",
    gauge: {
      name: "Kings River near Berryville",
      id: "07050500",  // Note: Fixed the ID to match URL
      url: "https://waterdata.usgs.gov/monitoring-location/07050500"
    },
    quality: "B",
    targetLevels: {
      tooLow: 2.85,
      optimal: 3.50,
      high: 5.00
    }
  },
  {
    name: "Illinois Bayou",
    rating: "II",
    size: "M",
    gauge: {
      name: "Illinois Bayou nr Scottsville",
      id: "07257500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07257500"
    },
    quality: "A",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.0
    }
  },
  {
    name: "Illinois R. (Hogeye Run)",
    rating: "II+",
    size: "S",
    gauge: {
      name: "Baron Fork at Dutch Mills",
      id: "07196900",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07196900"
    },
    quality: "C",
    targetLevels: {
      tooLow: 3.5,
      optimal: 5.0,
      high: 6.0
    }
  },
  {
    name: "Jack Cr.",
    rating: "II-III",
    size: "S",
    gauge: {
      name: "Dutch Cr. at Waltreak",
      id: "07260000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07260000"
    },
    quality: "C",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.5,
      high: 9.0
    }
  },
  {
    name: "Jordan Cr.",
    rating: "III+",
    size: "VS",
    gauge: {
      name: "Baron Fork at Dutch Mills",
      id: "07196900",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07196900"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.5,
      high: 8.0
    }
  },
  {
    name: "Lee Cr.",
    rating: "II+",
    size: "M",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.5,
      optimal: 5.5,
      high: 9.0
    }
  },
  {
    name: "Left Hand Prong",
    rating: "II-IV",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Little Mill Cr.",
    rating: "III-IV",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 7.5,
      optimal: 9.0,
      high: 11.0
    }
  },
  {
    name: "Little Missouri R.",
    rating: "II-III",
    size: "S",
    gauge: {
      name: "Little Missouri R. nr Langley",
      id: "07360200",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07360200"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.75,
      optimal: 6.0,
      high: 8.0
    }
  },
  {
    name: "Little Mulberry Cr.",
    rating: "III-IV",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 10.0
    }
  },
  {
    name: "Little Sugar Creek - Bella Vista",
    rating: "A",
    size: "M",
    gauge: {
      name: "Little Sugar Creek at Pineville",
      id: "07188838",
      url: "https://waterdata.usgs.gov/monitoring-location/07188838/"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.85,
      optimal: 4.50,
      high: 5.00
    }
  },
  {
    name: "Long Branch (EFLB)",
    rating: "III-V",
    size: "XS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Long Devils Fork Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Lower Saline R. (Play Waves)",
    rating: "PLAY",
    size: "DC",
    gauge: {
      name: "Saline River nr Dierks",
      id: "07341000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07341000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 6.0,
      optimal: 6.4,
      high: 11.0
    }
  },
  {
    name: "M. Fork Little Mill Cr.",
    rating: "III-IV",
    size: "XS",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 10.0,
      optimal: 11.0,
      high: 13.0
    }
  },
  {
    name: "M. Fork Little Red R.",
    rating: "II+",
    size: "M",
    gauge: {
      name: "Middle Fork nr Shirley",
      id: "07075000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07075000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 8.5,
      optimal: 9.5,
      high: 11.0
    }
  },
  {
    name: "Meadow Cr.",
    rating: "III+",
    size: "VS",
    gauge: {
      name: "Middle Fork nr Shirley",
      id: "07075000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07075000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 12.0,
      optimal: 13.0,
      high: 15.0
    }
  },
  {
    name: "Micro Cr.",
    rating: "III",
    size: "XS",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 12.0,
      optimal: 16.0,
      high: 25.0
    }
  },
  {
    name: "Mill Cr.",
    rating: "II-III+",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 8.0,
      high: 11.0
    }
  },
  {
    name: "Mormon Cr.",
    rating: "IV (IV+)",
    size: "XS",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 8.5,
      optimal: 10.5,
      high: 12.0
    }
  },
  {
    name: "Mulberry R. (above Hwy 23)",
    rating: "II",
    size: "L",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 1.9,
      optimal: 2.8,
      high: 5.0
    }
  },
  {
    name: "Mulberry R. (below Hwy 23)",
    rating: "I-II",
    size: "L",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 1.7,
      optimal: 2.3,
      high: 5.0
    }
  },
  {
    name: "Mystery Cr.",
    rating: "IV+ (V)",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 7.5,
      optimal: 9.0,
      high: 11.5
    }
  },
  {
    name: "Osage Cr.",
    rating: "III-IV",
    size: "S",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "D",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 9.5
    }
  },
  {
    name: "Pine Cr. OK",
    rating: "III+",
    size: "M",
    gauge: {
      name: "Pine Creek at Eubanks, OK",
      id: "07335840",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07335840"
    },
    quality: "A",
    targetLevels: {
      tooLow: 7.5,
      optimal: 8.0,
      high: 9.0
    }
  },
  {
    name: "Possum Walk Cr.",
    rating: "IV-V (P)",
    size: "S",
    gauge: {
      name: "Cadron Cr. nr Guy",
      id: "07261000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07261000"
    },
    quality: "F",
    targetLevels: {
      tooLow: 8.0,
      optimal: 10.0,
      high: 14.0
    }
  },
  {
    name: "Rattlesnake Cr.",
    rating: "IV (V)",
    size: "XS",
    gauge: {
      name: "Jack Cr. at Winfrey",
      id: "07250974",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07250974"
    },
    quality: "F",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.0,
      high: 7.5
    }
  },
  {
    name: "Richland Cr.",
    rating: "III-IV",
    size: "M",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.0,
      optimal: 4.0,
      high: 6.0
    }
  },
  {
    name: "Rock Cr.",
    rating: "II-III",
    size: "VS",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 7.5,
      optimal: 9.0,
      high: 11.5
    }
  },
  {
    name: "Rockport",
    rating: "PLAY",
    size: "DC",
    gauge: {
      name: "Ouachita R. bl Remmel Dam",
      id: "07359002",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07359002"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.5,
      optimal: 6.0,
      high: 7.0
    }
  },
  {
    name: "Roger's Private Idaho",
    rating: "II",
    size: "L",
    gauge: {
      name: "Strawberry R. nr Poughkeepsie",
      id: "07074000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07074000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.5,
      optimal: 3.7,
      high: 6.0
    }
  },
  {
    name: "Saint Francis R. (MO)",
    rating: "II-IV",
    size: "L",
    gauge: {
      name: "St. Francis River near Roselle",
      id: "07034000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07034000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.0,
      optimal: 4.0,
      high: 8.0
    }
  },
  {
    name: "Saline R.",
    rating: "II-III",
    size: "VS",
    gauge: {
      name: "Little Missouri R. nr Langley",
      id: "07360200",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07360200"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.0,
      high: 9.0
    }
  },
  {
    name: "Salt Fork",
    rating: "II-III",
    size: "S",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.5,
      high: 11.0
    }
  },
  {
    name: "Shoal Cr.",
    rating: "III",
    size: "VS",
    gauge: {
      name: "Dutch Cr. at Waltreak",
      id: "07260000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07260000"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.0,
      high: 9.5
    }
  },
  {
    name: "Shop Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 7.5,
      optimal: 8.5,
      high: 11.0
    }
  },
  {
    name: "Smith Cr.",
    rating: "III-V",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.5,
      high: 11.0
    }
  },
  {
    name: "South Fork Little Red R.",
    rating: "I-III",
    size: "M",
    gauge: {
      name: "S Fk Little Red R. at Clinton",
      id: "07075300",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07075300"
    },
    quality: "B",
    targetLevels: {
      tooLow: 5.5,
      optimal: 6.5,
      high: 8.0
    }
  },
  {
    name: "South Fourche Lafave R.",
    rating: "II+",
    size: "L",
    gauge: {
      name: "South Fourche LaFave nr Hollis",
      id: "07263000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07263000"
    },
    quality: "A",
    targetLevels: {
      tooLow: 3.5,
      optimal: 4.0,
      high: 6.0
    }
  },
  {
    name: "Spadra Cr.",
    rating: "III+",
    size: "M",
    gauge: {
      name: "Spadra Cr. at Clarksville",
      id: "07256500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07256500"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.0,
      optimal: 5.5,
      high: 8.0
    }
  },
  {
    name: "Spirits Cr.",
    rating: "III",
    size: "VS",
    gauge: {
      name: "Mulberry R. nr Mulberry",
      id: "07252000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07252000"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 8.0,
      optimal: 9.0,
      high: 11.0
    }
  },
  {
    name: "Spring River (Hardy)",
    rating: "II",
    size: "L",
    gauge: {
      name: "Spring River near Hardy, AR",
      id: "07069305",
      url: "https://waterdata.usgs.gov/monitoring-location/07069305/"
    },
    quality: "A",
    targetLevels: {
      tooLow: 2.99,
      optimal: 3.5,
      high: 4.0
    }
  },
  {
    name: "Stepp Cr.",
    rating: "III-IV+",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 6.5,
      optimal: 7.5,
      high: 10.0
    }
  },
  {
    name: "Sugar Cr.",
    rating: "II-III",
    size: "M",
    gauge: {
      name: "Dutch Cr. at Waltreak",
      id: "07260000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07260000"
    },
    quality: "C",
    targetLevels: {
      tooLow: 5.0,
      optimal: 6.0,
      high: 8.0
    }
  },
  {
    name: "Sulphur Cr.",
    rating: "IV-V+",
    size: "XS",
    gauge: {
      name: "Richland Cr. at Witts Springs",
      id: "07055875",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055875"
    },
    quality: "B+",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 8.5
    }
  },
  {
    name: "Tanyard Cr.",
    rating: "III-IV (V)",
    size: "VS",
    gauge: {
      name: "Spavinaw Creek near Cherokee",
      id: "07191179",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07191179"
    },
    quality: "F",
    targetLevels: {
      tooLow: 8.0,
      optimal: 9.0,
      high: 10.0
    }
  },
  {
    name: "Thomas Cr.",
    rating: "III-IV",
    size: "VS",
    gauge: {
      name: "Buffalo at Boxley",
      id: "07055646",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07055646"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 7.0,
      optimal: 8.5,
      high: 11.0
    }
  },
  {
    name: "Trigger Gap",
    rating: "PLAY",
    size: "L",
    gauge: {
      name: "Kings R. nr Berryville",
      id: "07050500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07050500"
    },
    quality: "A",
    targetLevels: {
      tooLow: 6.0,
      optimal: 7.0,
      high: 10.0
    }
  },
  {
    name: "Tulsa Wave",
    rating: "III",
    size: "DC",
    gauge: {
      name: "Arkansas River at Tulsa, OK",
      id: "07164500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07164500"
    },
    quality: "A",
    targetLevels: {
      tooLow: 10000,
      optimal: 10500,
      high: 15800
    }
  },
  {
    name: "Upper Upper Shoal Cr.",
    rating: "III+",
    size: "XS",
    gauge: {
      name: "Dutch Cr. at Waltreak",
      id: "07260000",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07260000"
    },
    quality: "D+",
    targetLevels: {
      tooLow: 9.0,
      optimal: 10.0,
      high: 11.5
    }
  },
  {
    name: "West Fork White River",
    rating: "I-II",
    size: "M",
    gauge: {
      name: "West Fork White River nr Fay",
      id: "07048550",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07048550"
    },
    quality: "A",
    targetLevels: {
      tooLow: 4.5,
      optimal: 6.0,
      high: 8.0
    }
  },
  {
    name: "West Horsehead Cr.",
    rating: "III-IV+",
    size: "XS",
    gauge: {
      name: "Spadra Cr. at Clarksville",
      id: "07256500",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07256500"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 9.0,
      optimal: 10.5,
      high: 14.0
    }
  },
  {
    name: "White R., Middle Fork",
    rating: "II",
    size: "S",
    gauge: {
      name: "White R. near Fayetteville",
      id: "07048600",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07048600"
    },
    quality: "F",
    targetLevels: {
      tooLow: 9.0,
      optimal: 10.0,
      high: 13.0
    }
  },
  {
    name: "White Rock Cr.",
    rating: "III-IV",
    size: "VS",
    gauge: {
      name: "Frog Bayou at Winfrey",
      id: "07250965",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07250965"
    },
    quality: "F",
    targetLevels: {
      tooLow: 13.0,
      optimal: 14.0,
      high: 16.0
    }
  },
  {
    name: "Whistlepost Cr.",
    rating: "IV-V (P)",
    size: "XS",
    gauge: {
      name: "Lee Cr. at Short, OK",
      id: "07249800",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249800"
    },
    quality: "C+",
    targetLevels: {
      tooLow: 14.0,
      optimal: 18.0,
      high: 22.0
    }
  },
  {
    name: "Wister Wave",
    rating: "III",
    size: "L",
    gauge: {
      name: "Poteau River near Panama, OK",
      id: "07249413",
      url: "http://waterdata.usgs.gov/nwis/uv/?site_no=07249413"
    },
    quality: "A",
    targetLevels: {
      tooLow: 11.5,
      optimal: 12.5,
      high: 13.5
    }
  }
];

```

# src/data/streamMetadata.ts

```ts
export const STREAM_METADATA = {
  sizeDefinitions: {
    XS: {
      width: '< 20ft',
      watershed: '< 1 sq mi',
      rainRate: '1.5 in/hr',
      window: '3-6 hrs'
    },
    VS: {
      width: '20-30ft',
      watershed: '1-4 sq mi',
      rainRate: '1.0 in/hr',
      window: '6-12 hrs'
    },
    S: {
      width: '30-40ft',
      watershed: '4-10 sq mi',
      rainRate: '0.75 in/hr',
      window: '1 day'
    },
    M: {
      width: '40-75ft',
      watershed: '10-25 sq mi',
      rainRate: '0.5 in/hr',
      window: '1-2 days'
    },
    L: {
      width: '> 75ft',
      watershed: '> 25 sq mi',
      rainRate: '0.2 in/hr',
      window: '2-5 days'
    },
    H: {
      width: '> 150ft',
      watershed: '> 75 sq mi',
      rainRate: '0.1 in/hr',
      window: '5+ days'
    },
    DC: {
      width: 'N/A',
      watershed: 'N/A',
      rainRate: 'N/A',
      window: 'Dam Controlled - Check Schedule!'
    },
    A: {
      width: 'N/A',
      watershed: 'N/A',
      rainRate: 'N/A',
      window: 'Always Runs'
    }
  },
  correlationQualityDefinitions: {
    'A': 'Excellent correlation. Gauge is on the creek near the run',
    'A+': 'Gauge is on a small creek and should be rising for a good run',
    'B': 'Good correlation. Creek is an upstream tributary to the gauged creek',
    'B+': 'Creek is a small upstream tributary to the gauged creek. Gauge should be rising',
    'C': 'Fair correlation. Creek is in a nearby watershed or downstream tributary',
    'C+': 'Same as C, but creek is small and gauge should be rising',
    'D': 'Poor correlation. Creek is weakly correlated to the gauge',
    'D+': 'Same as D, but creek is small and gauge should be rising',
    'F': 'No/Unknown correlation. Wild guess at best'
  },
  levelDefinitions: {
    tooLow: {
      code: 'X',
      color: '#FF0000',
      description: 'Creek is too low for fun paddling'
    },
    low: {
      code: 'L',
      color: '#FFFF00', 
      description: 'Creek is low but paddlable. May have to drag/portage in places'
    },
    optimal: {
      code: 'O',
      color: '#00FF00',
      description: 'Creek is perfect for paddling. The ratings listed are for this range'
    },
    high: {
      code: 'H',
      color: '#0000FF',
      description: 'Creek is high and potentially very dangerous. Many more hazards are present'
    }
  }
};
```

# src/hooks/useStreamGauge.ts

```ts
import { useState, useEffect } from 'react';
import { Stream, GaugeReading, LevelTrend } from '../types/stream';

export function useStreamGauge(stream: Stream) {
  const [reading, setReading] = useState<GaugeReading | null>(null);
  const [previousReading, setPreviousReading] = useState<GaugeReading | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchGaugeData = async () => {
      if (!stream.gauge.id) {
        setError(new Error('No gauge ID provided'));
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(
          `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=${stream.gauge.id}&parameterCd=00065`,
          {
            headers: {
              'Accept': 'application/json'
            }
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const latestReading = data.value.timeSeries[0].values[0].value[0];
        
        setReading(prevReading => {
          setPreviousReading(prevReading);
          return {
            value: parseFloat(latestReading.value),
            timestamp: latestReading.dateTime
          };
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch gauge data'));
      } finally {
        setLoading(false);
      }
    };

    fetchGaugeData();
    const interval = setInterval(fetchGaugeData, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, [stream.gauge.id]);

  const determineTrend = (): LevelTrend => {
    if (!reading || !previousReading) return LevelTrend.None;
    
    const difference = reading.value - previousReading.value;
    const THRESHOLD = 0.1; // Minimum change to consider rising/falling
    
    if (Math.abs(difference) < THRESHOLD) return LevelTrend.Holding;
    return difference > 0 ? LevelTrend.Rising : LevelTrend.Falling;
  };

  const currentLevel = reading ? {
    status: reading.value < stream.targetLevels.tooLow ? 'X' :
            reading.value < stream.targetLevels.optimal ? 'L' :
            reading.value < stream.targetLevels.high ? 'O' : 'H',
    trend: determineTrend()
  } : undefined;

  return {
    currentLevel,
    reading,
    loading,
    error
  };
}
```

# src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

```

# src/main.tsx

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);

```

# src/types/stream.ts

```ts
export interface GaugeReading {
  value: number;
  timestamp: string;
}

export enum LevelTrend {
  Rising = 'rise',
  Falling = 'fall',
  Holding = 'hold',
  None = 'none'
}

export interface Stream {
  id?: string;
  name: string;
  rating: string;
  size: string;
  gauge: {
    name: string;
    id: string;
    url: string;
  };
  quality: string;
  targetLevels: {
    tooLow: number;
    optimal: number;
    high: number;
  };
  currentLevel?: {
    status: string;  // 'X', 'L', 'O', 'H'
    trend: LevelTrend;
  };
}

export interface StreamData extends Stream {
  currentFlow?: number;
  temperature?: number;
  status?: string;
  lastUpdated?: string;
  waterQuality?: {
    ph: number;
    turbidity: number;
    dissolvedOxygen: number;
  };
}
```

# src/types/streamDefinitions.ts

```ts
// types/streamDefinitions.ts

/** Detailed size category definitions */
export const sizeDefinitions = {
  XS: {
    name: 'Extra Small',
    width: '< 20ft',
    watershed: '< 1 sq mi',
    rainRate: '1.5 in/hr',
    window: '3-6 hrs',
    description: 'Extra small creeks with very quick response to rain'
  },
  VS: {
    name: 'Very Small',
    width: '20-30ft',
    watershed: '1-4 sq mi',
    rainRate: '1.0 in/hr',
    window: '6-12 hrs',
    description: 'Very small creeks with quick response to rain'
  },
  S: {
    name: 'Small',
    width: '30-40ft',
    watershed: '4-10 sq mi',
    rainRate: '0.75 in/hr',
    window: '1 day',
    description: 'Small creeks with moderate response time'
  },
  M: {
    name: 'Medium',
    width: '40-75ft',
    watershed: '10-25 sq mi',
    rainRate: '0.5 in/hr',
    window: '1-2 days',
    description: 'Medium sized streams with longer response time'
  },
  L: {
    name: 'Large',
    width: '> 75ft',
    watershed: '> 25 sq mi',
    rainRate: '0.2 in/hr',
    window: '2-5 days',
    description: 'Large rivers with extended response time'
  },
  H: {
    name: 'Huge',
    width: '> 150ft',
    watershed: '> 75 sq mi',
    rainRate: '0.1 in/hr',
    window: '5+ days',
    description: 'Major rivers with very long response time'
  },
  DC: {
    name: 'Dam Controlled',
    width: 'N/A',
    watershed: 'N/A',
    rainRate: 'N/A',
    window: 'Scheduled',
    description: 'Flow controlled by dam releases - check schedule'
  },
  A: {
    name: 'Always Runs',
    width: 'N/A',
    watershed: 'N/A',
    rainRate: 'N/A',
    window: 'N/A',
    description: 'Consistent flow year-round'
  }
} as const;

/** Detailed correlation quality definitions */
export const correlationDefinitions = {
  'A': {
    name: 'Excellent',
    description: 'Excellent correlation. Gauge is on the creek near the run'
  },
  'A+': {
    name: 'Excellent Plus',
    description: 'Gauge is on a small creek and should be rising for a good run'
  },
  'B': {
    name: 'Good',
    description: 'Good correlation. Creek is an upstream tributary to the gauged creek'
  },
  'B+': {
    name: 'Good Plus',
    description: 'Creek is a small upstream tributary to the gauged creek. Gauge should be rising'
  },
  'C': {
    name: 'Fair',
    description: 'Fair correlation. Creek is in a nearby watershed or downstream tributary'
  },
  'C+': {
    name: 'Fair Plus',
    description: 'Same as Fair, but creek is small and gauge should be rising'
  },
  'D': {
    name: 'Poor',
    description: 'Poor correlation. Creek is weakly correlated to the gauge'
  },
  'D+': {
    name: 'Poor Plus',
    description: 'Same as Poor, but creek is small and gauge should be rising'
  },
  'F': {
    name: 'Unknown',
    description: 'No/Unknown correlation. Wild guess at best'
  }
} as const;

/** Water level condition definitions */
export const levelDefinitions = {
  tooLow: {
    name: 'Too Low',
    code: 'Too Low',
    color: '#FF0000',
    description: 'Creek is too low for fun paddling'
  },
  low: {
    name: 'Low',
    code: 'Low',
    color: '#FFFF00',
    description: 'Creek is low but paddlable. May have to drag/portage in places'
  },
  optimal: {
    name: 'Optimal',
    code: 'Optimal',
    color: '#00FF00',
    description: 'Creek is perfect for paddling. The ratings listed are for this range'
  },
  high: {
    name: 'High/Flood',
    code: 'High/Flood',
    color: '#0000FF',
    description: 'Creek is high and potentially very dangerous. Many more hazards are present in this range'
  }
} as const;

/** Detailed whitewater class rating definitions */
export const ratingDefinitions = {
  'I': {
    name: 'Class I - Easy',
    description: 'Fast moving water with riffles and small waves. Few obstacles, all obvious and easily missed with little training.',
    color: '#4caf50', // success.main
  },
  'II': {
    name: 'Class II - Novice',
    description: 'Straightforward rapids with wide, clear channels. Occasional maneuvering may be required.',
    color: '#81c784', // success.light
  },
  'III': {
    name: 'Class III - Intermediate',
    description: 'Rapids with moderate, irregular waves. Complex maneuvers in fast current and good boat control required.',
    color: '#ff9800', // warning.main
  },
  'IV': {
    name: 'Class IV - Advanced',
    description: 'Intense, powerful but predictable rapids requiring precise boat handling in turbulent water.',
    color: '#ef5350', // error.light
  },
  'V': {
    name: 'Class V - Expert',
    description: 'Extremely long, obstructed, or very violent rapids. Serious risks involved with rescue conditions difficult.',
    color: '#d32f2f', // error.main
  },
  'V+': {
    name: 'Class V+ - Extreme',
    description: 'These runs have almost never been attempted and often exemplify the extremes of difficulty, unpredictability and danger.',
    color: '#c62828', // error.dark
  }
} as const;

/** Type-safe helpers to get definitions */
export function getSizeDefinition(size: keyof typeof sizeDefinitions) {
  return sizeDefinitions[size];
}

export function getCorrelationDefinition(quality: keyof typeof correlationDefinitions) {
  return correlationDefinitions[quality];
}

export function getLevelDefinition(level: keyof typeof levelDefinitions) {
  return levelDefinitions[level];
}

/** Type-safe helper to get rating definition */
export function getRatingDefinition(rating: string) {
  // Handle combined ratings (e.g., "III-IV")
  if (rating.includes('-')) {
    const [lower, upper] = rating.split('-');
    return {
      name: `Class ${rating} - Mixed`,
      description: `Difficulty varies between ${ratingDefinitions[lower as keyof typeof ratingDefinitions]?.name} and ${ratingDefinitions[upper as keyof typeof ratingDefinitions]?.name} characteristics.`,
      color: ratingDefinitions[upper as keyof typeof ratingDefinitions]?.color || '#ff9800',
    };
  }

  // Handle plus ratings (e.g., "III+")
  if (rating.includes('+') && !rating.startsWith('V+')) {
    const baseRating = rating.replace('+', '') as keyof typeof ratingDefinitions;
    return {
      name: `Class ${rating} - Advanced ${ratingDefinitions[baseRating]?.name.split('-')[1]}`,
      description: `More demanding than ${baseRating} with some characteristics of the next higher class.`,
      color: ratingDefinitions[baseRating]?.color || '#ff9800',
    };
  }

  return ratingDefinitions[rating as keyof typeof ratingDefinitions] || {
    name: `Class ${rating}`,
    description: 'Rating information not available.',
    color: '#9e9e9e', // grey[500]
  };
}
```

# src/types/table.ts

```ts
// types/table.ts
export type SortDirection = 'asc' | 'desc';
export type SortField = 'name' | 'rating' | 'size' | 'gauge' | 'reading' | 'quality' | 'level' | 'trend';
```

# src/utils/sorting.ts

```ts
import { StreamData, LevelTrend } from '../types/stream';
import { SortDirection, SortField } from '../types/table';

// Helper function to get trend priority (Rising > Holding > Falling > None)
const getTrendPriority = (trend: LevelTrend | undefined): number => {
  switch (trend) {
    case LevelTrend.Rising: return 3;
    case LevelTrend.Holding: return 2;
    case LevelTrend.Falling: return 1;
    default: return 0;
  }
};

export function sortStreams(
  streams: StreamData[], 
  sortField: SortField, 
  sortDirection: SortDirection
): StreamData[] {
  return [...streams].sort((a, b) => {
    let comparison = 0;
    let trendA: number, trendB: number;

    switch (sortField) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'rating':
        comparison = a.rating.localeCompare(b.rating);
        break;
      case 'size':
        comparison = a.size.localeCompare(b.size);
        break;
      case 'gauge':
        comparison = a.gauge.name.localeCompare(b.gauge.name);
        break;
      case 'quality':
        comparison = a.quality.localeCompare(b.quality);
        break;
      case 'trend':
        trendA = getTrendPriority(a.currentLevel?.trend);
        trendB = getTrendPriority(b.currentLevel?.trend);
        comparison = trendB - trendA; // Higher priority first
        break;
      case 'level':
        if (a.currentLevel?.status && b.currentLevel?.status) {
          comparison = a.currentLevel.status.localeCompare(b.currentLevel.status);
        }
        break;
      case 'reading':
        const readingA = a.currentFlow ?? -Infinity;
        const readingB = b.currentFlow ?? -Infinity;
        comparison = readingA - readingB;
        break;
      default:
        comparison = 0;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });
}
```

# src/utils/streamLevels.ts

```ts
import { Stream } from '../types/stream';

export const determineLevel = (currentReading: number, targetLevels: Stream['targetLevels']) => {
  if (currentReading < targetLevels.tooLow) {
    return 'Too Low'; // Too Low
  } else if (currentReading < targetLevels.optimal) {
    return 'Low'; // Low
  } else if (currentReading < targetLevels.high) {
    return 'Optimal'; // Optimal
  } else {
    return 'High/Flood'; // High
  }
};

// Removed getLevelColor from here since it's now handled in the component
```

# src/vite-env.d.ts

```ts
/// <reference types="vite/client" />

```

# tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          main: '#1976d2',
          light: '#42a5f5',
          dark: '#1565c0',
          contrastText: '#fff',
        },
        secondary: {
          main: '#9c27b0',
          light: '#ba68c8',
          dark: '#7b1fa2',
          contrastText: '#fff',
        },
        error: {
          main: '#d32f2f',
          light: '#ef5350',
          dark: '#c62828',
          contrastText: '#fff',
        },
        warning: {
          main: '#ed6c02',
          light: '#ff9800',
          dark: '#e65100',
          contrastText: '#fff',
        },
        info: {
          main: '#0288d1',
          light: '#03a9f4',
          dark: '#01579b',
          contrastText: '#fff',
        },
        success: {
          main: '#2e7d32',
          light: '#4caf50',
          dark: '#1b5e20',
          contrastText: '#fff',
        },
        grey: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#eeeeee',
          300: '#e0e0e0',
          400: '#bdbdbd',
          500: '#9e9e9e',
          600: '#757575',
          700: '#616161',
          800: '#424242',
          900: '#212121',
        },
      },
      spacing: {
        // Material UI's spacing units (1 unit = 8px)
        0.5: '4px',
        1: '8px',
        2: '16px',
        3: '24px',
        4: '32px',
        5: '40px',
        6: '48px',
        7: '56px',
        8: '64px',
      },
      borderRadius: {
        // Material UI's default border radius values
        'none': '0',
        'sm': '4px',
        DEFAULT: '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
        '2xl': '16px',
      },
      fontFamily: {
        // Material UI's default font family
        sans: ['Roboto', 'Arial', 'sans-serif'],
      },
      fontSize: {
        // Material UI's typography scale
        xs: ['0.75rem', { lineHeight: '1.66' }],
        sm: ['0.875rem', { lineHeight: '1.43' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.125rem', { lineHeight: '1.5' }],
        xl: ['1.25rem', { lineHeight: '1.334' }],
        '2xl': ['1.5rem', { lineHeight: '1.334' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.167' }],
        '5xl': ['3rem', { lineHeight: '1.167' }],
      },
      boxShadow: {
        // Material UI's elevation levels
        1: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        2: '0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)',
        3: '0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)',
        4: '0 15px 25px rgba(0,0,0,0.15), 0 5px 10px rgba(0,0,0,0.05)',
        5: '0 20px 40px rgba(0,0,0,0.2)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

```

# tsconfig.app.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src", "useStreamAlerts.ts"]
}

```

# tsconfig.json

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}

```

# tsconfig.node.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["vite.config.ts"]
}

```

# vite.config.ts

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});

```

