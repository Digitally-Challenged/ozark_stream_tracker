import { useState } from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { DashboardSidebar } from './components/dashboard/DashboardSidebar';
import { ThemeProvider } from './context/ThemeContext';
import { GaugeDataProvider } from './context/GaugeDataContext';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { StreamPageLazy } from './pages/StreamPageLazy';

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
              <Header
                onFilterClick={() => setFilterOpen(!filterOpen)}
                filterOpen={filterOpen}
                activeFilterCount={
                  selectedRatings.length + selectedSizes.length
                }
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
                  <Route
                    path="/stream/:streamId"
                    element={<StreamPageLazy />}
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
