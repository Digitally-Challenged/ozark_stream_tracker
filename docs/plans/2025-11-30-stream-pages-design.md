# Stream Pages Design

## Overview

Link the stream markdown documentation files (`data/streams/*.md`) to the React UI via dedicated stream pages.

## Architecture

**Route & Navigation:**
- New route: `/stream/:streamId` (e.g., `/stream/buffalo-r`)
- Stream ID derived from markdown filename (e.g., `buffalo-r.md` → `buffalo-r`)
- Click stream name in table → navigates to stream page
- "Back to Dashboard" button on stream page

**Data Flow:**
1. Build time: Parse markdown files → TypeScript data
2. Runtime: Stream page fetches parsed content by ID
3. Render: Display sections (description, access points, rapids, images, etc.)

**File Structure:**
```
src/
  pages/
    StreamPage.tsx        # New dedicated stream page
  components/
    stream-page/
      StreamHeader.tsx    # Name, rating, current level
      StreamDescription.tsx
      StreamSections.tsx  # Access points, rapids, hazards
      StreamImages.tsx    # Image gallery
      StreamSources.tsx   # External links
  data/
    streamContent.generated.ts  # Parsed markdown → typed data
scripts/
  parse-streams.ts        # Build script to parse markdown
```

## UI Layout

```
┌─────────────────────────────────────────────┐
│ ← Back to Dashboard                         │
├─────────────────────────────────────────────┤
│ Buffalo National River          Class I-III │
│ ■ 2.45 ft  ▲ Rising  │ Optimal              │
├─────────────────────────────────────────────┤
│ ## Description                              │
│ Congress made this the first National...    │
├─────────────────────────────────────────────┤
│ ## Sections                                 │
│ • Upper Buffalo (Class II-III)              │
│ • Middle Buffalo (Class I-II)               │
│ • Lower Buffalo (Class I)                   │
├─────────────────────────────────────────────┤
│ ## Access Points                            │
│ Boxley → Pruitt → Gilbert → Buffalo City    │
├─────────────────────────────────────────────┤
│ ## Images                                   │
│ [photo] [photo] [photo]                     │
├─────────────────────────────────────────────┤
│ ## Hazards | ## Sources                     │
└─────────────────────────────────────────────┘
```

**Features:**
- Header shows live gauge data (reuses `useStreamGauge` hook)
- Collapsible sections for long content
- Image gallery with lightbox
- Mobile-responsive
- Dark mode compatible

## Data Types

```typescript
interface StreamContent {
  id: string;           // "buffalo-r"
  name: string;         // "Buffalo National River"
  overview: {
    rating: string;
    watershedSize: string;
    gradient: string;
    length: string;
    season: string;
  };
  description: string;
  sections: Section[];
  accessPoints: AccessPoint[];
  rapids: string[];
  hazards: string[];
  images: Image[];
  sources: Source[];
}

interface Section {
  name: string;
  distance?: string;
  rating?: string;
  gradient?: string;
  notes?: string;
}

interface AccessPoint {
  name: string;
  location?: string;
  directions?: string;
  notes?: string;
}

interface Image {
  url: string;
  alt: string;
  caption: string;
}

interface Source {
  title: string;
  url: string;
}
```

## Markdown Parsing

**Approach:** Pre-build script parses markdown → TypeScript

**Why pre-build:**
- No markdown parser in browser bundle
- Type-safe at compile time
- Faster page loads

**Script:** `scripts/parse-streams.ts`
- Runs before build via npm script
- Outputs `src/data/streamContent.generated.ts`
- Generated file is git-ignored

---

## Implementation Tasks

### Task 1: Set up markdown parsing infrastructure
- [ ] Create `scripts/parse-streams.ts`
- [ ] Add markdown parsing dependencies (gray-matter, marked)
- [ ] Define TypeScript interfaces in `src/types/streamContent.ts`
- [ ] Add npm script: `"prebuild": "ts-node scripts/parse-streams.ts"`

### Task 2: Implement markdown parser
- [ ] Parse frontmatter (overview section)
- [ ] Extract description (## Description)
- [ ] Parse sections (## Sections)
- [ ] Parse access points (## Access Points)
- [ ] Parse rapids, hazards, images, sources
- [ ] Generate `streamContent.generated.ts`

### Task 3: Create StreamPage component
- [ ] Set up React Router route `/stream/:streamId`
- [ ] Create `src/pages/StreamPage.tsx`
- [ ] Add back navigation to dashboard
- [ ] Integrate with `useStreamGauge` for live data

### Task 4: Build stream page sections
- [ ] `StreamHeader.tsx` - name, rating, live gauge
- [ ] `StreamDescription.tsx` - main prose
- [ ] `StreamSections.tsx` - river sections list
- [ ] `StreamAccessPoints.tsx` - access points
- [ ] `StreamImages.tsx` - image gallery
- [ ] `StreamSources.tsx` - external links

### Task 5: Link from dashboard
- [ ] Make stream name clickable in `StreamTableRow.tsx`
- [ ] Use React Router `Link` component
- [ ] Update existing `StreamDetail` dialog (keep or remove?)

### Task 6: Polish & test
- [ ] Mobile responsiveness
- [ ] Dark mode styling
- [ ] Test with multiple streams
- [ ] Handle missing content gracefully
