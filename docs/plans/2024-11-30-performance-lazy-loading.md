# Performance: Lazy Load Stream Content Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce initial bundle size by lazy-loading stream content pages, improving first contentful paint.

**Architecture:** Use React.lazy() and Suspense to dynamically import StreamPage component. The stream content (150KB) will only load when user navigates to a stream detail page.

**Tech Stack:** React 18, React Router, Vite code splitting

---

## Current State

- Main bundle: 208 KB (includes stream content)
- Stream content: ~150 KB (90 streams)
- All content loads on initial page load even if user never views stream pages

## Target State

- Main bundle: ~60 KB (dashboard only)
- Stream content: Lazy-loaded on demand
- Users see dashboard faster, content loads when needed

---

## Tasks

### Task 1: Create Lazy StreamPage Wrapper

**Files:**

- Create: `src/pages/StreamPageLazy.tsx`

**Step 1: Create lazy wrapper component**

Create new file `src/pages/StreamPageLazy.tsx`:

```typescript
import { lazy, Suspense } from 'react';
import { Box, CircularProgress, Container } from '@mui/material';

const StreamPage = lazy(() => import('./StreamPage'));

function LoadingFallback() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh',
        }}
      >
        <CircularProgress />
      </Box>
    </Container>
  );
}

export function StreamPageLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <StreamPage />
    </Suspense>
  );
}
```

**Step 2: Verify file created correctly**

Run: `cat src/pages/StreamPageLazy.tsx`
Expected: File contents match above

**Step 3: Commit**

```bash
git add src/pages/StreamPageLazy.tsx
git commit -m "feat: add lazy-loaded StreamPage wrapper

Prepares for code splitting stream content into separate chunk."
```

---

### Task 2: Convert StreamPage to Default Export

**Files:**

- Modify: `src/pages/StreamPage.tsx`

**Step 1: Change named export to default export**

At the end of `src/pages/StreamPage.tsx`, find:

```typescript
export function StreamPage() {
```

Change to:

```typescript
export default function StreamPage() {
```

**Step 2: Verify the change compiles**

Run: `npm run build`
Expected: Build succeeds (may show warnings about chunk size, which is expected)

**Step 3: Commit**

```bash
git add src/pages/StreamPage.tsx
git commit -m "refactor: convert StreamPage to default export

Required for React.lazy() dynamic import."
```

---

### Task 3: Update Router to Use Lazy Component

**Files:**

- Modify: `src/App.tsx`

**Step 1: Update import statement**

Find at top of file:

```typescript
import { StreamPage } from './pages/StreamPage';
```

Replace with:

```typescript
import { StreamPageLazy } from './pages/StreamPageLazy';
```

**Step 2: Update Route element**

Find in Routes section:

```typescript
<Route path="/stream/:streamId" element={<StreamPage />} />
```

Replace with:

```typescript
<Route path="/stream/:streamId" element={<StreamPageLazy />} />
```

**Step 3: Verify the change compiles and splits correctly**

Run: `npm run build`

Expected output should show separate chunk for StreamPage:

```
dist/assets/StreamPage-[hash].js   ~150+ kB
```

**Step 4: Commit**

```bash
git add src/App.tsx
git commit -m "feat: lazy load stream pages for better initial load

Stream content now loads only when user navigates to a stream page.
Reduces initial bundle by ~150KB."
```

---

### Task 4: Verify Code Splitting Works

**Step 1: Build production bundle**

Run: `npm run build`

**Step 2: Check bundle output**

Run: `ls -lh dist/assets/*.js`

Expected: Should see new StreamPage chunk file separate from main index.js

**Step 3: Compare bundle sizes**

The main `index-*.js` should be smaller than before (~60KB instead of ~208KB).
A new `StreamPage-*.js` chunk should exist (~150KB).

**Step 4: Test in browser**

Run: `npm run preview`

1. Open Network tab in DevTools
2. Navigate to dashboard - verify StreamPage chunk NOT loaded
3. Click on a stream link - verify StreamPage chunk loads
4. Verify stream page displays correctly with loading spinner during load

**Step 5: Final commit**

```bash
git add -A
git commit -m "chore: verify lazy loading implementation complete"
```

---

## Rollback Plan

If issues arise, revert by:

1. Change `StreamPageLazy` back to `StreamPage` in App.tsx import
2. Delete `StreamPageLazy.tsx`
3. Change `export default function` back to `export function` in StreamPage.tsx

---

## Future Enhancements (Out of Scope)

1. **Prefetch on hover**: Preload stream content when user hovers over link
2. **Route-based code splitting**: Split dashboard components as well
3. **Missing content**: Create content for Caddo R., Camp Cr., Dragover, Ellis Cr., Saint Francis R.
