import { Box, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { ThemeProvider } from './context/ThemeContext';
import { GaugeDataProvider } from './context/GaugeDataContext';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { StreamPageLazy } from './pages/StreamPageLazy';
import { PrecipitationMapLazy } from './pages/PrecipitationMapLazy';

function ErrorFallback({ error }: { error: Error }) {
  return (
    <Box sx={{ p: 4 }}>
      <h2>Something went wrong:</h2>
      <pre>{error.message}</pre>
    </Box>
  );
}

function App() {
  return (
    <GaugeDataProvider>
      <ThemeProvider>
        <CssBaseline />
        <BrowserRouter>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              minHeight: '100vh',
              bgcolor: (theme) =>
                theme.palette.mode === 'dark' ? '#1a1a1a' : '#f5f5f5',
            }}
          >
            <ErrorBoundary FallbackComponent={ErrorFallback}>
              <Header />
              <Box sx={{ display: 'flex', flex: 1 }}>
                <Routes>
                  <Route
                    path="/"
                    element={<Navigate to="/dashboard" replace />}
                  />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route
                    path="/stream/:streamId"
                    element={<StreamPageLazy />}
                  />
                  <Route
                    path="/precipitation"
                    element={<PrecipitationMapLazy />}
                  />
                </Routes>
              </Box>
              <Footer />
            </ErrorBoundary>
          </Box>
        </BrowserRouter>
      </ThemeProvider>
    </GaugeDataProvider>
  );
}

export default App;
