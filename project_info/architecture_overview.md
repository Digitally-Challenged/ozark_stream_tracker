# Architecture Overview

## Frontend Framework & Build System
- **Framework**: React `18.3.1` with TypeScript `5.5.3`.
- **Build Tool**: Vite `5.4.2`.
- **Language Features**: Utilizes functional components, React Hooks, JSX/TSX.
- **Strict Mode**: `React.StrictMode` is enabled in `src/main.tsx` for development checks.

## Styling
- **Primary UI Component Library**: Material UI (`@mui/material`) is used for core components (Dialogs, Tables, Paper, Theming). It uses Emotion (`@emotion/react`, `@emotion/styled`) for styling its components.
- **Utility CSS Framework**: Tailwind CSS is also integrated and configured in `tailwind.config.js` to align with Material UI's theme settings (colors, spacing, fonts). This dual approach will be reviewed for optimization.
- **Icons**: Both `lucide-react` and `@mui/icons-material` are used.

## Application Structure
- **Entry Point**: `src/main.tsx` initializes the React application and renders the main `App` component.
- **Main Application Component**: `src/App.tsx` sets up:
    - Global theme provider (`ThemeProvider` from `src/context/ThemeContext.tsx`).
    - `CssBaseline` from MUI for style normalization.
    - `BrowserRouter` from `react-router-dom` for routing.
    - Top-level layout including `Header`, `Footer`, and a `DashboardSidebar`.
    - Error boundaries (`ErrorBoundary` from `react-error-boundary`).
- **Routing**: Managed by `react-router-dom`. Currently, a simple setup redirects from `/` to `/dashboard`.
    - `DashboardContent` (defined in `App.tsx`) is the main view, displaying stream data.
- **State Management**:
    - Global state for theme: React Context (`ThemeContext`).
    - Component-level state (`useState`) for UI interactions (e.g., selected stream in `DashboardContent`, filter sidebar visibility in `App`).
    - Data fetching and state related to external data is encapsulated in custom hooks (e.g., `useStreamGauge`).
- **Data**:
    - Static application data (stream definitions, metadata) is located in `src/data/`.
    - Dynamic data is fetched from external APIs (USGS).

## Key Directories
- `src/components/`: Contains UI components, organized by feature area (core, dashboard, streams).
- `src/context/`: Houses React Context providers (e.g., `ThemeContext`).
- `src/data/`: Static data for the application.
- `src/hooks/`: Custom React Hooks.
- `src/types/`: TypeScript type definitions.
- `src/utils/`: Utility functions.
```
