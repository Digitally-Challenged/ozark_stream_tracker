const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { TurnerBendScraperService, setupAPI } = require('./turnerBendScraper');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for frontend (stricter in production)
const allowedOrigins =
  process.env.NODE_ENV === 'production'
    ? ['https://ozark-stream-tracker.netlify.app']
    : [
        'http://localhost:5174',
        'http://localhost:5175',
        'https://ozark-stream-tracker.netlify.app',
      ];

app.use(
  cors({
    origin: allowedOrigins,
    credentials: true,
  })
);

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: { error: 'Too many requests' },
});

const scrapeLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  message: { error: 'Scrape rate limit exceeded' },
});

app.use('/api/', apiLimiter);

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Setup Turner Bend API endpoints (with scrape rate limiting)
setupAPI(app, scrapeLimiter);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message:
      process.env.NODE_ENV === 'development'
        ? err.message
        : 'Something went wrong',
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
