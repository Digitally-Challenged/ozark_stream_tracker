const https = require('https');
const cheerio = require('cheerio');

// In-memory cache for Netlify Functions (persists across warm invocations)
let cachedData = null;
let cacheTimestamp = 0;
const CACHE_DURATION_MS = 15 * 60 * 1000; // 15 minutes

function fetchHtml(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(
      url,
      {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; OzarkStreamTracker/1.0)',
        },
        timeout: 10000,
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => resolve(data));
      }
    );
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timed out'));
    });
  });
}

async function scrapeWaterLevel() {
  const url = 'https://www.turnerbend.com/WaterLevel.html';

  const html = await fetchHtml(url);
  const $ = cheerio.load(html);
  const pageText = $('body').text();

  let waterLevel = null;
  let date = new Date().toISOString();
  let description = '';

  // Look for water level patterns - handles date-level concatenation
  const levelMatch = pageText.match(
    /\d{1,2}-\d{1,2}-\d{4}\s*(\d{1,2}\.\d+)\s*['"]|(?<!\d)(\d{1,2}\.\d+)\s*['"]|Level:\s*(\d+\.?\d*)|Water\s*Level:\s*(\d+\.?\d*)/i
  );

  if (levelMatch) {
    const parsed = parseFloat(
      levelMatch[1] || levelMatch[2] || levelMatch[3] || levelMatch[4]
    );
    if (!isNaN(parsed) && parsed >= 0) {
      waterLevel = parsed;
    }
  }

  // Look for date information
  const dateMatch = pageText.match(/(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/);
  if (dateMatch) {
    try {
      const parsedDate = new Date(dateMatch[1]);
      if (!isNaN(parsedDate.getTime())) {
        date = parsedDate.toISOString();
      }
    } catch (e) {
      // Keep default date
    }
  }

  // Check for conditions
  if (pageText.toLowerCase().includes('dry weather')) {
    description = 'Dry weather conditions';
  } else if (pageText.toLowerCase().includes('rain')) {
    description = 'Recent rainfall';
  } else if (pageText.toLowerCase().includes('flood')) {
    description = 'Flood conditions';
  }

  if (waterLevel === null) {
    throw new Error('Could not find water level in HTML');
  }

  return {
    level: waterLevel,
    unit: 'ft',
    timestamp: date,
    dateTime: date,
    source: 'Turner Bend Landing',
    lastUpdated: date,
    description,
  };
}

async function getCurrentData(forceScrape = false) {
  const now = Date.now();

  // Return cached data if still fresh
  if (!forceScrape && cachedData && now - cacheTimestamp < CACHE_DURATION_MS) {
    return { ...cachedData, cached: true };
  }

  // Scrape fresh data
  const data = await scrapeWaterLevel();
  cachedData = data;
  cacheTimestamp = now;

  return { ...data, cached: false };
}

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin':
      process.env.URL || 'https://ozarkcreekflowzone.com',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const path = event.path
    .replace('/.netlify/functions/turner-bend', '')
    .replace('/api/turner-bend', '');

  try {
    // GET /current - get current reading
    if (
      event.httpMethod === 'GET' &&
      (path === '/current' || path === '' || path === '/')
    ) {
      const data = await getCurrentData();
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(data),
      };
    }

    // POST /scrape - force fresh scrape (requires auth)
    if (event.httpMethod === 'POST' && path === '/scrape') {
      const authHeader = event.headers?.authorization || '';
      const expected = process.env.SCRAPE_TOKEN;
      if (!expected || authHeader !== `Bearer ${expected}`) {
        return {
          statusCode: 401,
          headers,
          body: JSON.stringify({ error: 'Unauthorized' }),
        };
      }
      const data = await getCurrentData(true);
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify(data),
      };
    }

    return {
      statusCode: 404,
      headers,
      body: JSON.stringify({ error: 'Endpoint not found' }),
    };
  } catch (error) {
    console.error('Turner Bend function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Failed to get Turner Bend data',
        timestamp: new Date().toISOString(),
      }),
    };
  }
};
