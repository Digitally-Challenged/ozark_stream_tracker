const axios = require('axios');
const cheerio = require('cheerio');
const cron = require('node-cron');
const fs = require('fs').promises;
const path = require('path');

class TurnerBendScraperService {
  constructor() {
    this.url = 'https://www.turnerbend.com/WaterLevel.html';
    this.dataFile = path.join(__dirname, 'turner-bend-data.json');
  }

  async scrapeWaterLevel() {
    try {
      console.log(`[${new Date().toISOString()}] Starting Turner Bend scrape...`);
      
      const response = await axios.get(this.url, {
        timeout: 10000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; OzarkStreamTracker/1.0)'
        }
      });

      const $ = cheerio.load(response.data);
      
      // Parse the water level from Turner Bend website (REAL DATA ONLY)
      let waterLevel = null;
      let date = new Date().toISOString();
      let description = '';

      // Get the full page text for parsing
      const pageText = $('body').text();
      console.log('Turner Bend page content preview:', pageText.substring(0, 500));
      
      // Look for water level patterns like "0.8'" or "2.5 feet"
      // FIXED: Handles date-level concatenation (e.g., "12-03-20252.2'" -> 2.2)
      // Pattern breakdown:
      // 1. Date followed by level (handles MM-DD-YYYYx.x' concatenation)
      // 2. Standalone level not preceded by digit
      // 3. "Level: X.X" format
      // 4. "Water Level: X.X" format
      const levelMatch = pageText.match(
        /\d{1,2}-\d{1,2}-\d{4}\s*(\d{1,2}\.\d+)\s*['"]|(?<!\d)(\d{1,2}\.\d+)\s*['"]|Level:\s*(\d+\.?\d*)|Water\s*Level:\s*(\d+\.?\d*)/i
      );
      if (levelMatch) {
        const parsed = parseFloat(levelMatch[1] || levelMatch[2] || levelMatch[3] || levelMatch[4]);
        if (!isNaN(parsed) && parsed >= 0) {
          waterLevel = parsed;
          console.log('Found water level:', waterLevel, 'from match:', levelMatch[0]);
        }
      }
      
      // Look for date information in format like "9-17-2025"
      const dateMatch = pageText.match(/(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/);
      if (dateMatch) {
        try {
          const parsedDate = new Date(dateMatch[1]);
          if (!isNaN(parsedDate.getTime())) {
            date = parsedDate.toISOString();
            console.log('Found date:', dateMatch[1], 'parsed as:', date);
          }
        } catch (e) {
          console.warn('Date parsing failed:', e.message);
        }
      }
      
      // Look for descriptive text about conditions
      if (pageText.toLowerCase().includes('dry weather')) {
        description = 'Dry weather conditions';
      } else if (pageText.toLowerCase().includes('rain')) {
        description = 'Recent rainfall';
      } else if (pageText.toLowerCase().includes('flood')) {
        description = 'Flood conditions';
      }

      if (!waterLevel) {
        throw new Error('Could not find water level in HTML - check website structure');
      }

      const data = {
        level: waterLevel,
        unit: 'ft',
        timestamp: date,
        dateTime: date,
        source: 'Turner Bend Landing',
        lastUpdated: date,
        description
      };

      // Save to file
      await this.saveData(data);
      
      console.log(`[${new Date().toISOString()}] Scrape successful:`, data);
      return data;
    } catch (error) {
      console.error(`[${new Date().toISOString()}] Scrape failed:`, error.message);
      throw error;
    }
  }

  async saveData(data) {
    try {
      const history = await this.loadHistory();
      history.push({
        ...data,
        scrapedAt: new Date().toISOString()
      });
      
      // Keep only last 30 days of data
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      
      const filteredHistory = history.filter(entry => 
        new Date(entry.scrapedAt) > thirtyDaysAgo
      );

      await fs.writeFile(this.dataFile, JSON.stringify({
        current: data,
        history: filteredHistory
      }, null, 2));
    } catch (error) {
      console.error('Error saving data:', error);
    }
  }

  async loadHistory() {
    try {
      const data = await fs.readFile(this.dataFile, 'utf8');
      const parsed = JSON.parse(data);
      return parsed.history || [];
    } catch (error) {
      return [];
    }
  }

  async getCurrentData() {
    try {
      const data = await fs.readFile(this.dataFile, 'utf8');
      const parsed = JSON.parse(data);
      return parsed.current;
    } catch (error) {
      console.warn('No cached Turner Bend data available');
      return null;
    }
  }

  startScheduler() {
    // Run immediately on start
    this.scrapeWaterLevel().catch(console.error);

    // Schedule to run every 4 hours (more frequent for safety)
    cron.schedule('0 */4 * * *', async () => {
      await this.scrapeWaterLevel();
    });

    console.log('Turner Bend scraper scheduled for every 4 hours');
  }
}

// Express API endpoint setup
function setupAPI(app, scrapeLimiter = null) {
  const scraper = new TurnerBendScraperService();
  
  app.get('/api/turner-bend/current', async (req, res) => {
    try {
      const data = await scraper.getCurrentData();
      if (data) {
        res.json(data);
      } else {
        // Try to scrape if no data exists
        const freshData = await scraper.scrapeWaterLevel();
        res.json(freshData);
      }
    } catch (error) {
      console.error('Turner Bend API error:', error);
      res.status(500).json({
        error: 'Failed to get Turner Bend data',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An internal error occurred',
        timestamp: new Date().toISOString()
      });
    }
  });

  // Apply scrape rate limiter if provided
  const scrapeMiddleware = scrapeLimiter ? [scrapeLimiter] : [];
  app.post('/api/turner-bend/scrape', ...scrapeMiddleware, async (req, res) => {
    try {
      const data = await scraper.scrapeWaterLevel();
      res.json(data);
    } catch (error) {
      console.error('Turner Bend scrape error:', error);
      res.status(500).json({
        error: 'Failed to scrape Turner Bend data',
        message: process.env.NODE_ENV === 'development' ? error.message : 'An internal error occurred',
        timestamp: new Date().toISOString()
      });
    }
  });

  // Start the scheduler
  scraper.startScheduler();
  
  console.log('Turner Bend API endpoints configured');
}

// Standalone mode
if (require.main === module) {
  const scraper = new TurnerBendScraperService();
  scraper.startScheduler();
}

module.exports = { TurnerBendScraperService, setupAPI };