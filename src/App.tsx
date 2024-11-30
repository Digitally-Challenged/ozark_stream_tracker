import React, { useState } from 'react';
import { Box, Container, CssBaseline } from '@mui/material';
import { Header } from './components/core/Header';
import { Footer } from './components/core/Footer';
import { StreamTable } from './components/streams/StreamTable';
import { StreamDetail } from './components/streams/StreamDetail';
import { DashboardHeader } from './components/dashboard/DashboardHeader';
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
    <>
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
    </>
  );
}

function App() {
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
            <Header />
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardContent />} />
            </Routes>
            <Footer />
          </ErrorBoundary>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
