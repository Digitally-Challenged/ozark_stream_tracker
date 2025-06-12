// API Configuration
export const API_CONFIG = {
  USGS_BASE_URL: 'https://waterservices.usgs.gov/nwis/iv/',
  GAUGE_HEIGHT_PARAMETER: '00065',
  REFRESH_INTERVAL_MS: 15 * 60 * 1000, // 15 minutes
  REQUEST_TIMEOUT_MS: 10000,
  MAX_RETRIES: 3,
  RETRY_DELAY_MS: 1000,
} as const;

// Stream Level Configuration
export const STREAM_LEVELS = {
  CHANGE_THRESHOLD: 0.1,
  FRESHNESS_HOURS: {
    VERY_FRESH: 1.5,
    FRESH: 3.0,
    RECENT: 10.0,
  },
} as const;

// Filter Options
export const FILTER_OPTIONS = {
  RATINGS: [
    { value: 'all', label: 'All Ratings' },
    { value: '5', label: '5 Stars' },
    { value: '4', label: '4 Stars' },
    { value: '3', label: '3 Stars' },
    { value: '2', label: '2 Stars' },
    { value: '1', label: '1 Star' },
  ],
  SIZES: [
    { value: 'all', label: 'All Sizes' },
    { value: 'small', label: 'Small' },
    { value: 'medium', label: 'Medium' },
    { value: 'large', label: 'Large' },
  ],
} as const;

// UI Configuration
export const UI_CONFIG = {
  TABLE_PAGE_SIZE: 10,
  TABLE_PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
  SIDEBAR_FILTER_MAX_HEIGHT: 224,
  DEBOUNCE_DELAY_MS: 300,
  ANIMATION_DURATION_MS: 300,
} as const;

// Theme Configuration
export const THEME_CONFIG = {
  DEFAULT_MODE: 'dark' as const,
  STORAGE_KEY: 'ozark-stream-tracker-theme',
} as const;

// Date/Time Configuration
export const DATE_CONFIG = {
  DEFAULT_LOCALE: 'en-US',
  TIME_FORMAT: 'PPpp',
  SHORT_TIME_FORMAT: 'p',
  DATE_FORMAT: 'PP',
} as const;

// Level Status Configuration
export const LEVEL_STATUS = {
  VERY_HIGH: 'Very High',
  HIGH: 'High',
  GOOD: 'Good',
  LOW: 'Low',
  VERY_LOW: 'Very Low',
  UNKNOWN: 'Unknown',
} as const;

// Level Colors (MUI palette colors)
export const LEVEL_COLORS = {
  [LEVEL_STATUS.VERY_HIGH]: 'error',
  [LEVEL_STATUS.HIGH]: 'warning',
  [LEVEL_STATUS.GOOD]: 'success',
  [LEVEL_STATUS.LOW]: 'info',
  [LEVEL_STATUS.VERY_LOW]: 'default',
  [LEVEL_STATUS.UNKNOWN]: 'default',
} as const;

// Storage Keys
export const STORAGE_KEYS = {
  THEME: THEME_CONFIG.STORAGE_KEY,
  FILTER_RATINGS: 'ozark-stream-tracker-filter-ratings',
  FILTER_SIZES: 'ozark-stream-tracker-filter-sizes',
  SORT_COLUMN: 'ozark-stream-tracker-sort-column',
  SORT_DIRECTION: 'ozark-stream-tracker-sort-direction',
} as const;