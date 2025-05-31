# API Integration

This document details the external services and APIs used by the application.

## USGS Water Services API

- **Purpose**: Used to fetch real-time hydrological data for streams, specifically gauge height (parameter code `00065`).
- **Endpoint**: `https://waterservices.usgs.gov/nwis/iv/` (Instantaneous Values Web Service)
- **Implementation**:
  - The `useStreamGauge` custom hook (`src/hooks/useStreamGauge.ts`) is responsible for interacting with this API.
  - It constructs a request URL like: `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=<GAUGE_ID>&parameterCd=00065`.
  - The `<GAUGE_ID>` is taken from the `stream.gauge.id` property of the stream object.
- **Data Format**:
  - Requests JSON format (`format=json`).
  - The hook expects a specific structure in the JSON response to extract the latest gauge reading (`data.value.timeSeries[0].values[0].value[0]`).
- **Fetching Mechanism**:
  - Uses the `fetch` API.
  - Fetches data when the component using the hook mounts.
  - Implements an interval timer to refresh data every 15 minutes.
- **Error Handling**:
  - Checks if `response.ok` and throws an error for non-successful HTTP statuses.
  - Catches errors during the fetch operation and stores them in the `error` state variable of the hook.
- **Authentication**: No authentication is required for this public API.

## Other Potential Integrations

- Currently, no other external APIs are evidently integrated.
- Future considerations might include:
  - Weather APIs for rainfall data.
  - GIS services for map-based stream views.

```

```
