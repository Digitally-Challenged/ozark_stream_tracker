const express = require('express');
const cors = require('cors');
const { TurnerBendScraperService, setupAPI } = require('./turnerBendScraper');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for frontend
app.use(cors({
  origin: ['http://localhost:5174', 'http://localhost:5175', 'https://ozark-stream-tracker.netlify.app'],
  credentials: true
}));

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Setup Turner Bend API endpoints
setupAPI(app);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

app.listen(PORT, () => {
  console.log(`🌊 Turner Bend scraper server running on port ${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   GET  /api/turner-bend/current - Get latest reading`);
  console.log(`   POST /api/turner-bend/scrape  - Trigger fresh scrape`);
  console.log(`   GET  /health                  - Health check`);
});