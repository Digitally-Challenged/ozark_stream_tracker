# Stream ID Mapping Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix stream name to content ID mapping so each dashboard stream links to the correct detail page (or shows no link if no content exists).

**Architecture:** Replace fuzzy string matching with an explicit lookup table that maps exact stream names from `streamData.ts` to their corresponding content IDs in `streamContent.generated.ts`. This eliminates false-positive matches like "Rock Cr." incorrectly linking to "gutter-rock-cr".

**Tech Stack:** TypeScript, React Router

---

## Problem Summary

Current `getStreamIdFromName()` in `src/utils/streamIds.ts` uses aggressive fuzzy matching:
- `includes()` causes "Rock Cr." to match "gutter-rock-cr"
- First-word matching causes "Sugar Cr." to match "little-sugar-creek"
- 5 streams have no content, 9+ have incorrect duplicate mappings

## Tasks

### Task 1: Create Explicit Stream Name to ID Mapping

**Files:**
- Modify: `src/utils/streamIds.ts`

**Step 1: Replace fuzzy matching with explicit mapping table**

Replace the entire file contents with:

```typescript
import { getAllStreamIds } from '../data/streamContent.generated';

// Explicit mapping from streamData names to content IDs
// Only streams with dedicated content pages are listed here
const STREAM_NAME_TO_ID: Record<string, string> = {
  // Exact matches (stream name matches content ID pattern)
  'Adkins Cr.': 'adkins-cr',
  'Archey Cr.': 'archey-cr',
  'Baker Cr.': 'baker-cr',
  'Bear Cr.': 'bear-cr',
  'Beech Cr.': 'beech-cr',
  'Ben Doodle Cr.': 'ben-doodle-cr',
  'Big Devils Fork Cr.': 'big-devils-fork-cr',
  'Blackburn Cr.': 'blackburn-cr',
  'Bobtail Cr.': 'bobtail-cr',
  'Boss Hollow': 'boss-hollow',
  'Boulder Cr.': 'boulder-cr',
  'Cadron Cr.': 'cadron-cr',
  'Cedar Cr.': 'cedar-cr',
  'Clear Cr.': 'clear-cr',
  'Crooked Cr.': 'crooked-cr',
  'Fall Cr.': 'fall-cr',
  'Falling Water Cr.': 'falling-water-cr',
  'Falls Br.': 'falls-br',
  'Fern Gulley': 'fern-gulley',
  'Frog Bayou': 'frog-bayou',
  'Gutter Rock Cr.': 'gutter-rock-cr',
  'Hailstone Cr.': 'hailstone-cr',
  'Hart Cr.': 'hart-cr',
  'Haw Cr.': 'haw-cr',
  'Illinois Bayou': 'illinois-bayou',
  'Jack Cr.': 'jack-cr',
  'Jordan Cr.': 'jordan-cr',
  'Lee Cr.': 'lee-cr',
  'Left Hand Prong': 'left-hand-prong',
  'Little Mill Cr.': 'little-mill-cr',
  'Little Mulberry Cr.': 'little-mulberry-cr',
  'Long Devils Fork Cr.': 'long-devils-fork-cr',
  'M. Fork Little Mill Cr.': 'm-fork-little-mill-cr',
  'M. Fork Little Red R.': 'm-fork-little-red-r',
  'Meadow Cr.': 'meadow-cr',
  'Micro Cr.': 'micro-cr',
  'Mill Cr.': 'mill-cr',
  'Mormon Cr.': 'mormon-cr',
  'Mystery Cr.': 'mystery-cr',
  'Osage Cr.': 'osage-cr',
  'Possum Walk Cr.': 'possum-walk-cr',
  'Rattlesnake Cr.': 'rattlesnake-cr',
  'Rock Cr.': 'rock-cr',
  'Salt Fork': 'salt-fork',
  'Shoal Cr.': 'shoal-cr',
  'Shop Cr.': 'shop-cr',
  'Smith Cr.': 'smith-cr',
  'Spadra Cr.': 'spadra-cr',
  'Spirits Cr.': 'spirits-cr',
  'Stepp Cr.': 'stepp-cr',
  'Sugar Cr.': 'sugar-cr',
  'Sulphur Cr.': 'sulphur-cr',
  'Tanyard Cr.': 'tanyard-cr',
  'Thomas Cr.': 'thomas-cr',
  'Trigger Gap': 'trigger-gap',
  'Upper Upper Shoal Cr.': 'upper-upper-shoal-cr',
  'West Horsehead Cr.': 'west-horsehead-cr',
  'Whistlepost Cr.': 'whistlepost-cr',
  'White Rock Cr.': 'white-rock-cr',

  // Rivers with sections - map to main river page
  'Big Piney Cr (abv Longpool)': 'big-piney-cr',
  'Big Piney Cr (blw Longpool)': 'big-piney-cr',
  'Buffalo R. (Boxley Valley)': 'buffalo-r',
  'Buffalo R. (below Ponca)': 'buffalo-r',
  'Buffalo R. at Ponca': 'buffalo-r',
  'Cossatot R.': 'cossatot-r',
  'E. Fk. White R.': 'e-fk-white-r',
  'Hurricane Cr. (Franklin)': 'hurricane-cr-franklin',
  'Hurricane Cr. (Newton)': 'hurricane-cr-newton',
  'Illinois R. (Hogeye Run)': 'illinois-r',
  'Kings River (lower)': 'kings-river',
  'Little Missouri R.': 'little-missouri-r',
  'Little Sugar Creek - Bella Vista': 'little-sugar-creek',
  'Long Branch (EFLB)': 'long-branch',
  'Lower Saline R. (Play Waves)': 'lower-saline-r',
  'Mulberry R. (Turner Bend)': 'mulberry-r',
  'Mulberry R. (above Hwy 23)': 'mulberry-r',
  'Mulberry R. (below Hwy 23)': 'mulberry-r',
  'Pine Cr. OK': 'pine-cr-ok',
  'Richland Cr.': 'richland-cr',
  'Saline R.': 'saline-r',
  'South Fork Little Red R.': 'south-fork-little-red-r',
  'South Fourche Lafave R.': 'south-fourche-lafave-r',
  'Spring River (Hardy)': 'spring-river',
  'Tulsa Wave': 'tulsa-wave',
  'West Fork White River': 'west-fork-white-river',
  'White R., Middle Fork': 'white-r-middle-fork',
  'Wister Wave': 'wister-wave',

  // EFLB special case
  'EFLB': 'eflb',
};

// Validate mappings on module load (development only)
if (import.meta.env.DEV) {
  const allIds = new Set(getAllStreamIds());
  for (const [name, id] of Object.entries(STREAM_NAME_TO_ID)) {
    if (!allIds.has(id)) {
      console.warn(`[streamIds] Invalid mapping: "${name}" -> "${id}" (content ID not found)`);
    }
  }
}

/**
 * Convert a stream name to its corresponding content ID.
 * Returns null if no content page exists for this stream.
 */
export function getStreamIdFromName(name: string): string | null {
  return STREAM_NAME_TO_ID[name] ?? null;
}
```

**Step 2: Verify the fix compiles**

Run: `npm run build`
Expected: Build succeeds with no TypeScript errors

**Step 3: Commit**

```bash
git add src/utils/streamIds.ts
git commit -m "fix: replace fuzzy stream ID matching with explicit lookup table

- Eliminates incorrect matches (Rock Cr. -> gutter-rock-cr, etc.)
- Streams without content now show no link instead of wrong link
- Add dev-mode validation to catch invalid mappings"
```

---

### Task 2: Add Missing Content Marker for Unlinked Streams

**Files:**
- Modify: `src/components/streams/StreamTableRow.tsx:74-97`

**Step 1: Update stream name cell to show visual indicator when no content exists**

Find this code block (lines 74-97):

```typescript
{/* Stream Name */}
<TableCell>
  {(() => {
    const streamId = getStreamIdFromName(stream.name);
    return streamId ? (
      <Link
        component={RouterLink}
        to={`/stream/${streamId}`}
        onClick={(e) => e.stopPropagation()}
        sx={{
          color: theme.palette.text.primary,
          textDecoration: 'none',
          fontWeight: 500,
          '&:hover': {
            color: theme.palette.primary.main,
            textDecoration: 'underline',
          },
        }}
      >
        {stream.name}
      </Link>
    ) : (
      stream.name
    );
  })()}
</TableCell>
```

Replace with:

```typescript
{/* Stream Name */}
<TableCell>
  {(() => {
    const streamId = getStreamIdFromName(stream.name);
    return streamId ? (
      <Link
        component={RouterLink}
        to={`/stream/${streamId}`}
        onClick={(e) => e.stopPropagation()}
        sx={{
          color: theme.palette.text.primary,
          textDecoration: 'none',
          fontWeight: 500,
          '&:hover': {
            color: theme.palette.primary.main,
            textDecoration: 'underline',
          },
        }}
      >
        {stream.name}
      </Link>
    ) : (
      <Typography
        component="span"
        sx={{
          fontWeight: 500,
          color: theme.palette.text.secondary,
        }}
      >
        {stream.name}
      </Typography>
    );
  })()}
</TableCell>
```

**Step 2: Verify the fix compiles**

Run: `npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add src/components/streams/StreamTableRow.tsx
git commit -m "fix: show muted text for streams without content pages

Streams without dedicated content now display with secondary text color
instead of appearing as broken links."
```

---

### Task 3: Unify Status Badge Colors

**Files:**
- Modify: `src/components/stream-page/StreamHeader.tsx:29-42`

**Step 1: Replace hardcoded hex colors with MUI theme tokens**

Find this code block (lines 29-42):

```typescript
function getStatusColor(status: string): string {
  switch (status) {
    case 'X':
      return '#e57373'; // red - too low
    case 'L':
      return '#ffb74d'; // orange - low
    case 'O':
      return '#81c784'; // green - optimal
    case 'H':
      return '#64b5f6'; // blue - high
    default:
      return '#9e9e9e'; // grey
  }
}
```

Replace with:

```typescript
function getStatusColor(status: string, theme: ReturnType<typeof useTheme>): string {
  switch (status) {
    case 'X':
      return theme.palette.error.main;
    case 'L':
      return theme.palette.warning.main;
    case 'O':
      return theme.palette.success.main;
    case 'H':
      return theme.palette.info.main;
    default:
      return theme.palette.grey[500];
  }
}
```

**Step 2: Update the function call (line 160)**

Find:
```typescript
bgcolor: getStatusColor(status),
```

Replace with:
```typescript
bgcolor: getStatusColor(status, theme),
```

**Step 3: Verify the fix compiles**

Run: `npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add src/components/stream-page/StreamHeader.tsx
git commit -m "fix: unify status badge colors with MUI theme

Use theme.palette tokens instead of hardcoded hex values for consistency
with dashboard status colors."
```

---

### Task 4: Manual Testing Verification

**Step 1: Start dev server**

Run: `npm run dev`

**Step 2: Test fixed mappings**

Navigate to dashboard and verify:
- [ ] "Rock Cr." shows no link (not linked to gutter-rock-cr)
- [ ] "Sugar Cr." shows no link (not linked to little-sugar-creek)
- [ ] "Gutter Rock Cr." links to correct page
- [ ] "Big Piney Cr (abv Longpool)" and "(blw Longpool)" both link to big-piney-cr
- [ ] Caddo R., Camp Cr., Ellis Cr. show muted text (no content)

**Step 3: Test dark mode colors**

Toggle dark mode and verify status badges use consistent theme colors.

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: verify UI audit fixes complete"
```

---

## Streams Without Content (Future Work)

These 5 streams need markdown content files created:
1. Caddo R.
2. Camp Cr.
3. Dragover (Ouachita R.)
4. Ellis Cr.
5. Saint Francis R. (MO)

This is out of scope for this plan but documented for follow-up.
