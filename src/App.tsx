import { useState, useEffect } from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { DashboardSidebar } from './components/dashboard/DashboardSidebar';
import { ThemeProvider } from './context/ThemeContext';
import { GaugeDataProvider } from './context/GaugeDataContext';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { ScraperScheduler } from './services/scraperScheduler';

function ErrorFallback({ error }: { error: Error }) {
  return (
    <Box sx={{ p: 4 }}>
      <h2>Something went wrong:</h2>
      <pre>{error.message}</pre>
    </Box>
  );
}

function App() {
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedRatings, setSelectedRatings] = useState<string[]>([]);
  const [selectedSizes, setSelectedSizes] = useState<string[]>([]);

  useEffect(() => {
    // Start the Turner Bend scraper scheduler
    ScraperScheduler.start();

    // Cleanup on unmount
    return () => {
      ScraperScheduler.stop();
    };
  }, []);

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
              theme.palette.mode === 'dark' ? '#121212' : '#f5f5f5',
          }}
        >
          <ErrorBoundary FallbackComponent={ErrorFallback}>
            <Header
              onFilterClick={() => setFilterOpen(!filterOpen)}
              filterOpen={filterOpen}
            />
            <Box sx={{ display: 'flex', flex: 1 }}>
              <Routes>
                <Route
                  path="/"
                  element={<Navigate to="/dashboard" replace />}
                />
                <Route
                  path="/dashboard"
                  element={
                    <DashboardPage
                      selectedRatings={selectedRatings}
                      selectedSizes={selectedSizes}
                    />
                  }
                />
              </Routes>
            </Box>
            <DashboardSidebar
              open={filterOpen}
              onClose={() => setFilterOpen(false)}
              selectedRatings={selectedRatings}
              setSelectedRatings={setSelectedRatings}
              selectedSizes={selectedSizes}
              setSelectedSizes={setSelectedSizes}
            />
            <Footer />
          </ErrorBoundary>
        </Box>
        </BrowserRouter>
      </ThemeProvider>
    </GaugeDataProvider>
  );
}

export default App;
