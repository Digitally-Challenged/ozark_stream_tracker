import React, { useState } from 'react';
import { Box, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { DashboardSidebar } from './components/dashboard/DashboardSidebar';
import { ThemeProvider } from './context/ThemeContext';
import { ErrorBoundary } from 'react-error-boundary';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage'; // New import

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
  const [selectedRatings, setSelectedRatings] = useState<string[]>([]); // Added
  const [selectedSizes, setSelectedSizes] = useState<string[]>([]); // Added

  return (
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
                      selectedRatings={selectedRatings} // Added
                      selectedSizes={selectedSizes} // Added
                    />
                  }
                />
              </Routes>
            </Box>
            <DashboardSidebar
              open={filterOpen}
              onClose={() => setFilterOpen(false)}
              selectedRatings={selectedRatings} // Added
              setSelectedRatings={setSelectedRatings} // Added
              selectedSizes={selectedSizes} // Added
              setSelectedSizes={setSelectedSizes} // Added
            />
            <Footer />
          </ErrorBoundary>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
