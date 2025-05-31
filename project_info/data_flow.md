# Data Flow Overview

This document outlines how data is managed and flows through the application.

## State Management
- **Global State**:
    - **Theme**: Managed by `ThemeContext` (`src/context/ThemeContext.tsx`). Provides `mode` (dark/light) and `toggleColorMode` function to consuming components. `App.tsx` wraps the application in `ThemeProvider`.
- **Component-Level State**:
    - Managed using `useState` hook within individual components. Examples:
        - `App.tsx`: `filterOpen` (boolean) to control sidebar visibility.
        - `DashboardContent` (in `App.tsx`): `selectedStream` (StreamData | null) to manage which stream's details are shown.
        - `StreamTable.tsx`: `sortField`, `sortDirection`, `searchTerm` for table operations.
- **Custom Hooks for Data Fetching State**:
    - `useStreamGauge.ts`: Encapsulates the logic for fetching stream gauge data from the USGS API. It manages its own state for `reading`, `previousReading`, `loading`, and `error`, and derives `currentLevel` and `trend`.

## Data Passing
- **Props**: Primary mechanism for passing data down the component tree.
    - Example: `streams` data from `src/data/streamData.ts` is passed from `App.tsx` (via `DashboardContent`) to `StreamTable.tsx`.
    - Example: `selectedStream` is passed from `DashboardContent` to `StreamDetail.tsx`.
    - Callbacks are passed as props for child-to-parent communication (e.g., `onStreamClick` from `StreamTable` to `DashboardContent`, `onClose` for `StreamDetail`).
- **React Context**: Used for the theme, making it available to any component without prop drilling.

## External Data
- **USGS API**:
    - The `useStreamGauge` hook fetches live stream gauge data (flow rate - parameter `00065`) from `https://waterservices.usgs.gov/nwis/iv/`.
    - Data is fetched on component mount and then at a 15-minute interval.
    - The hook processes this data to provide current reading, previous reading, loading/error states, and derived level/trend information.
- **Static Data**:
    - `src/data/streamData.ts`: Contains an array of `StreamData` objects, defining the list of streams known to the application, their properties, and target water levels. This data is currently hardcoded.
    - `src/data/streamMetadata.ts` & `src/types/streamDefinitions.ts`: Contain definitions and metadata for stream characteristics like size, quality, rating, and levels. This is used by `StreamInfoTooltip.tsx` and other components to provide descriptive information.

## Data Transformation
- **Sorting**: `src/utils/sorting.ts` provides `sortStreams` function used by `StreamTable.tsx` to sort the stream list based on user selection.
- **Level Determination**:
    - `useStreamGauge.ts` determines the current level status ('X', 'L', 'O', 'H') based on the fetched reading and `targetLevels` for the stream.
    - `src/utils/streamLevels.ts` (specifically `determineLevel` function, though its direct usage seems superseded by logic within `useStreamGauge` and `StreamTableRow` for color) was intended for this.
- **Date Formatting**: `date-fns` library is used in `StreamDetail.tsx` to format date strings.
```
