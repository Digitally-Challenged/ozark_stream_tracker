# Hooks Analysis

This document provides a detailed analysis of custom React hooks used in the application.

## `useStreamGauge.ts`

- **Location**: `src/hooks/useStreamGauge.ts`

- **Purpose**:

  - Fetches real-time stream gauge data (specifically gauge height, parameter code `00065`) for a given stream from the USGS Water Services API.
  - Manages state related to the data fetching lifecycle (loading, error, data).
  - Determines the current water level status (Too Low, Low, Optimal, High/Flood) and trend (Rising, Falling, Holding) based on the fetched data and the stream's target levels.
  - Provides this information to the component that uses the hook.

- **Interface (`GaugeState`)**:

  ```typescript
  interface GaugeState {
    currentLevel?: {
      status: LevelStatus; // e.g., 'X', 'L', 'O', 'H'
      trend: LevelTrend; // e.g., 'rise', 'fall', 'hold'
    };
    reading: GaugeReading | null; // Contains value (number) and timestamp (string)
    loading: boolean;
    error: Error | null;
  }
  ```

  The hook itself takes a `stream: StreamData` object as an argument.

- **State Management**:

  - `state: GaugeState` (useState): A single state object holding `currentLevel`, `reading`, `loading`, and `error`. Initialized with `loading: true` and null for other fields.
  - `previousReading: GaugeReading | null` (useState): Stores the reading from the prior successful fetch to help determine the trend. Initialized to `null`.

- **Side Effects & Data Fetching (within `useEffect`)**:

  - **API Call**: Performs a `fetch` request to the USGS API endpoint: `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=<SITE_ID>&parameterCd=00065`.
  - **Data Parsing**: Parses the JSON response to extract the gauge reading value and timestamp.
  - **Interval Fetching**: Sets up an interval (`setInterval`) to re-fetch data every 15 minutes.
  - **Cleanup**:
    - Clears the interval on component unmount or when `stream.gauge.id` changes.
    - Uses an `AbortController` to cancel ongoing fetch requests during cleanup.
    - Uses a `mounted` flag to prevent state updates on unmounted components, although the AbortController and the nature of `useEffect` cleanup often make this redundant if dependencies are correct.

- **Key Functions/Logic**:

  - **`useEffect` Hook**:
    - Triggers on component mount and when `stream.gauge.id` changes.
    - Contains the `fetchGaugeData` async function.
  - **`fetchGaugeData` async function**:
    - Handles the API request and response.
    - Sets loading state.
    - On successful fetch:
      - Updates `previousReading` with the value of `state.reading` from the _previous_ state.
      - Calculates `status` using `determineLevel(newReading.value, stream.targetLevels)`.
      - Calculates `trend` using `determineTrend(newReading, previousReading)`.
      - Updates the main `state` object with the new reading, calculated level/trend, and resets loading/error.
    - Handles errors by setting the `error` state.
  - **Helper Functions (imported from `../utils/streamLevels`)**:
    - `determineLevel(currentReading: number, targetLevels: Stream['targetLevels'])`: Determines level status.
    - `determineTrend(currentReading: GaugeReading, previousReading: GaugeReading | null)`: Determines level trend.

- **Dependencies**:

  - **Types**:
    - `StreamData`, `GaugeReading`, `LevelStatus`, `LevelTrend` (from `../types/stream`).
  - **Utility Functions**:
    - `determineLevel`, `determineTrend` (from `../utils/streamLevels`).
  - **React**:
    - `useState`, `useEffect`.

- **AI Bloat Indicators / Areas for Optimization & Review**:

  - **State Update for `previousReading`**: `setPreviousReading(state.reading);` happens just before `setState` for the main state. Since `state.reading` is from the _current_ render's state (which is about to be updated), this correctly captures the reading that _was_ current before the _new_ reading is set. This seems correct.
  - **Error Handling**: Good basic error handling for API request failures.
  - **`mounted` flag**: The use of a `mounted` variable is a common pattern to prevent state updates on unmounted components, especially with intervals or promises. However, modern React practices with `AbortController` and proper `useEffect` cleanup (which are present) often mitigate the need for manual `mounted` flags. If all async operations are correctly cancelled in the cleanup, direct state updates after unmount shouldn't occur. It doesn't hurt, but might be slightly redundant.
  - **Initial State**: `currentLevel` is undefined in the initial state. Components using this hook need to handle this undefined case until the first successful data fetch.
  - **Parameter Code**: The parameter code `00065` (gauge height in feet) is hardcoded. If other parameters were needed, this would need to be made dynamic. For its current purpose, this is fine.
  - **API Response Structure Dependency**: The hook directly accesses nested properties of the API response (`data.value.timeSeries[0].values[0].value[0]`). Any change in the USGS API response structure would break this. This is a common vulnerability when dealing with external APIs. Adding more robust parsing or a library like Zod for response validation could be considered for extreme production hardening, but is likely overkill for this project's current scope.

- **Overall Assessment**:
  - A well-structured and crucial custom hook that encapsulates the logic for fetching and processing external stream data.
  - Implements important features like interval fetching and cleanup.
  - The logic for determining level and trend is delegated to utility functions, which is good for separation of concerns.
  - The recent refactor to a single state object (`GaugeState`) is a good pattern.

```

```
