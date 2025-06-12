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
      
      // Parse the water level - adjust these selectors based on actual HTML structure
      // Example selectors - these need to be updated based on the actual HTML
      let waterLevel = null;
      let date = new Date().toISOString();
      let description = '';

      // Look for water level in various possible formats
      // This is a placeholder - you'll need to inspect the actual HTML
      $('body').find('*').each((i, elem) => {
        const text = $(elem).text();
        // Look for patterns like "2.5'" or "2.5 feet"
        const match = text.match(/(\d+\.?\d*)\s*['"]|(\d+\.?\d*)\s*fe?e?t/i);
        if (match && !waterLevel) {
          waterLevel = parseFloat(match[1] || match[2]);
        }
      });

      if (!waterLevel) {
        throw new Error('Could not find water level in HTML');
      }

      const data = {
        level: waterLevel,
        unit: 'ft',
        timestamp: date,
        dateTime: date,
        source: 'Turner Bend Landing',
        lastUpdated: date
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
      return null;
    }
  }

  startScheduler() {
    // Run immediately on start
    this.scrapeWaterLevel().catch(console.error);

    // Schedule to run every day at 6 AM and 6 PM
    cron.schedule('0 6,18 * * *', async () => {
      await this.scrapeWaterLevel();
    });

    console.log('Turner Bend scraper scheduled for 6 AM and 6 PM daily');
  }
}

// Express API endpoint (if using Express)
function setupAPI(app) {
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
      res.status(500).json({ error: 'Failed to get Turner Bend data' });
    }
  });

  app.post('/api/turner-bend/scrape', async (req, res) => {
    try {
      const data = await scraper.scrapeWaterLevel();
      res.json(data);
    } catch (error) {
      res.status(500).json({ error: 'Failed to scrape Turner Bend data' });
    }
  });

  // Start the scheduler
  scraper.startScheduler();
}

// Standalone mode
if (require.main === module) {
  const scraper = new TurnerBendScraperService();
  scraper.startScheduler();
}

module.exports = { TurnerBendScraperService, setupAPI };