# Turner Bend Scraper Setup Guide

## Overview
The Turner Bend gauge reading requires web scraping since there's no official government API. This guide explains how to set up the scraping system.

## Architecture

### 1. Client-Side (React App)
- **Location**: `src/services/turnerBendScraper.ts`
- Attempts to fetch from backend API first
- Falls back to cached/mock data if API unavailable
- Caches data for 15 minutes locally

### 2. Client-Side Scheduler
- **Location**: `src/services/scraperScheduler.ts`
- Runs in the browser (not ideal for production)
- Attempts to scrape every 24 hours
- Stores last scrape timestamp

### 3. Backend Scraper Service (Recommended)
- **Location**: `server/turnerBendScraper.js`
- Node.js service that scrapes the Turner Bend website
- Runs on a schedule (6 AM and 6 PM daily)
- Provides API endpoints for the frontend

## Setup Instructions

### Option 1: Client-Side Only (Development)
No additional setup needed. The app will use mock data when the Turner Bend gauge is displayed.

### Option 2: Full Backend Setup (Production)

1. **Install Backend Dependencies**
   ```bash
   cd server
   npm install
   ```

2. **Start the Backend Service**
   ```bash
   npm start
   ```
   The service will run on port 3001 by default.

3. **Configure Frontend**
   Create a `.env` file in the root directory:
   ```
   REACT_APP_API_URL=http://localhost:3001/api/turner-bend/current
   ```

4. **Deploy to Production**
   - Deploy the backend service to a server (Heroku, AWS, etc.)
   - Update `REACT_APP_API_URL` to point to your production API
   - Consider using environment variables for different environments

### Option 3: Serverless Function
You can also deploy the scraper as a serverless function (AWS Lambda, Vercel, etc.) that runs on a schedule.

## API Endpoints

- `GET /api/turner-bend/current` - Get the latest cached reading
- `POST /api/turner-bend/scrape` - Trigger a manual scrape

## Troubleshooting

### CORS Issues
- The backend service includes CORS headers
- For development, you may need to configure proxy in `package.json`

### Scraping Failures
- Check the HTML structure of turnerbend.com hasn't changed
- Update the selectors in `server/turnerBendScraper.js` if needed
- Check server logs for specific error messages

### Data Not Updating
- Check `localStorage` for 'turner-bend-last-scrape' timestamp
- Verify the backend service is running
- Check network tab for API calls

## Monitoring
- The scraper logs all attempts and results
- Failed scrapes are logged with error details
- Historical data is kept for 30 days