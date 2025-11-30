import { TurnerBendScraper } from './turnerBendScraper';

export class ScraperScheduler {
  private static intervalId: NodeJS.Timeout | null = null;
  private static readonly SCRAPE_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours
  private static readonly INITIAL_DELAY = 5000; // 5 seconds after app start

  static start(): void {
    // Stop any existing scheduler
    this.stop();

    // Initial scrape after a short delay
    setTimeout(() => {
      this.performScrape();
    }, this.INITIAL_DELAY);

    // Set up recurring scrape every 24 hours
    this.intervalId = setInterval(() => {
      this.performScrape();
    }, this.SCRAPE_INTERVAL);
  }

  static stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private static async performScrape(): Promise<void> {
    try {
      console.log('[ScraperScheduler] Starting Turner Bend scrape...');
      const data = await TurnerBendScraper.fetchGaugeData();

      if (data) {
        console.log(
          '[ScraperScheduler] Successfully scraped Turner Bend data:',
          data
        );
        // Store timestamp of last successful scrape
        localStorage.setItem(
          'turner-bend-last-scrape',
          new Date().toISOString()
        );
      } else {
        console.error('[ScraperScheduler] Failed to scrape Turner Bend data');
      }
    } catch (error) {
      console.error('[ScraperScheduler] Error during scrape:', error);
    }
  }

  static getLastScrapeTime(): string | null {
    return localStorage.getItem('turner-bend-last-scrape');
  }

  static async scrapeNow(): Promise<void> {
    await this.performScrape();
  }
}
