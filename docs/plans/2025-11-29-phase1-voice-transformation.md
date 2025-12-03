# Phase 1: Stream Description Voice Transformation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform 89 stream markdown files from dry, factual descriptions to engaging narratives written in a folksy Ozark river guide voice (Billy Bob Thornton meets Sam Elliott).

**Architecture:** Each stream file's `## Description` section (and optionally `## Hazards`) will be rewritten using the voice prompt at `data/streams/_VOICE_PROMPT.md`. All structured data (Overview, Access Points, Rapids, Sources) remains unchanged.

**Tech Stack:** Markdown files, Claude agents for voice transformation

---

## Pre-Work: Voice Prompt Reference

**Voice Prompt Location:** `/Users/COLEMAN/Documents/GitHub/ozark_stream_tracker/data/streams/_VOICE_PROMPT.md`

**Voice Characteristics:**

- Folksy but not dumb - plain language with occasional poetry
- Dry wit - understated humor, lets facts speak
- Respects the river - reverence, not fear-mongering
- Straight-talking - no corporate speak, no hype
- Rhythmic - sentences have a cadence, like firelight storytelling

**Do:** Use "you/you'll", let rapid names speak, include texture (colors/sounds), mention uniqueness, end with wisdom

**Don't:** Exclamation points, "thrilling/exciting/adventure", over-explain ratings, sound like a brochure, add info not in source

---

## Task 1: Batch A - Streams adkins through boss-hollow (12 files)

**Files to Process:**

- `data/streams/adkins-cr.md`
- `data/streams/archey-cr.md`
- `data/streams/baker-cr.md`
- `data/streams/bear-cr.md`
- `data/streams/beech-cr.md`
- `data/streams/ben-doodle-cr.md`
- `data/streams/big-devils-fork-cr.md`
- `data/streams/big-piney-cr.md`
- `data/streams/blackburn-cr.md`
- `data/streams/bobtail-cr.md`
- `data/streams/boss-hollow.md`
- `data/streams/boulder-cr.md`

**Step 1: Read voice prompt**

Read: `data/streams/_VOICE_PROMPT.md`
Internalize the voice characteristics, do's, don'ts, and example transformation.

**Step 2: Process each file**

For each file in the batch:

1. **Read** the current markdown file
2. **Identify** the `## Description` section
3. **Rewrite** the description using the voice:
   - Keep all facts from the original
   - Transform dry language to folksy narrative
   - Add texture (colors, sounds, what water does)
   - End with practical wisdom if appropriate
4. **Optionally enhance** the `## Hazards` section with dry wit
5. **Preserve** all other sections exactly as-is
6. **Write** the updated file back

**Step 3: Verify transformations**

For each file, confirm:

- Description section has been transformed
- No information was lost
- No exclamation points or forbidden words ("thrilling", "exciting", "adventure")
- Structured data sections unchanged
- Sources preserved

**Step 4: Commit batch**

```bash
git add data/streams/adkins-cr.md data/streams/archey-cr.md data/streams/baker-cr.md data/streams/bear-cr.md data/streams/beech-cr.md data/streams/ben-doodle-cr.md data/streams/big-devils-fork-cr.md data/streams/big-piney-cr.md data/streams/blackburn-cr.md data/streams/bobtail-cr.md data/streams/boss-hollow.md data/streams/boulder-cr.md
git commit -m "feat: add voice to stream descriptions (batch A: adkins-boulder)"
```

---

## Task 2: Batch B - Streams buffalo through eflb (8 files)

**Files to Process:**

- `data/streams/buffalo-r.md`
- `data/streams/cadron-cr.md`
- `data/streams/cedar-cr.md`
- `data/streams/clear-cr.md`
- `data/streams/cossatot-r.md`
- `data/streams/crooked-cr.md`
- `data/streams/e-fk-white-r.md`
- `data/streams/eflb.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/buffalo-r.md data/streams/cadron-cr.md data/streams/cedar-cr.md data/streams/clear-cr.md data/streams/cossatot-r.md data/streams/crooked-cr.md data/streams/e-fk-white-r.md data/streams/eflb.md
git commit -m "feat: add voice to stream descriptions (batch B: buffalo-eflb)"
```

---

## Task 3: Batch C - Streams fall through hurricane-cr (13 files)

**Files to Process:**

- `data/streams/fall-cr.md`
- `data/streams/falling-water-cr.md`
- `data/streams/falls-br.md`
- `data/streams/fern-gulley.md`
- `data/streams/fishers-ford.md`
- `data/streams/frog-bayou.md`
- `data/streams/gutter-rock-cr.md`
- `data/streams/hailstone-cr.md`
- `data/streams/hart-cr.md`
- `data/streams/haw-cr.md`
- `data/streams/hurricane-cr-franklin.md`
- `data/streams/hurricane-cr-newton.md`
- `data/streams/hurricane-cr.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/fall-cr.md data/streams/falling-water-cr.md data/streams/falls-br.md data/streams/fern-gulley.md data/streams/fishers-ford.md data/streams/frog-bayou.md data/streams/gutter-rock-cr.md data/streams/hailstone-cr.md data/streams/hart-cr.md data/streams/haw-cr.md data/streams/hurricane-cr-franklin.md data/streams/hurricane-cr-newton.md data/streams/hurricane-cr.md
git commit -m "feat: add voice to stream descriptions (batch C: fall-hurricane)"
```

---

## Task 4: Batch D - Streams illinois through little-sugar (14 files)

**Files to Process:**

- `data/streams/illinois-bayou.md`
- `data/streams/illinois-r.md`
- `data/streams/illinois-river.md`
- `data/streams/jack-cr.md`
- `data/streams/jordan-cr.md`
- `data/streams/kings-river.md`
- `data/streams/lee-cr.md`
- `data/streams/left-hand-prong.md`
- `data/streams/little-mill-cr.md`
- `data/streams/little-missouri-r.md`
- `data/streams/little-mulberry-cr.md`
- `data/streams/little-piney-cr.md`
- `data/streams/little-sugar-creek.md`
- `data/streams/long-branch.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/illinois-bayou.md data/streams/illinois-r.md data/streams/illinois-river.md data/streams/jack-cr.md data/streams/jordan-cr.md data/streams/kings-river.md data/streams/lee-cr.md data/streams/left-hand-prong.md data/streams/little-mill-cr.md data/streams/little-missouri-r.md data/streams/little-mulberry-cr.md data/streams/little-piney-cr.md data/streams/little-sugar-creek.md data/streams/long-branch.md
git commit -m "feat: add voice to stream descriptions (batch D: illinois-long-branch)"
```

---

## Task 5: Batch E - Streams long-devils through mulberry (14 files)

**Files to Process:**

- `data/streams/long-devils-fork-cr.md`
- `data/streams/lower-saline-r.md`
- `data/streams/m-fork-little-mill-cr.md`
- `data/streams/m-fork-little-red-r.md`
- `data/streams/meadow-cr.md`
- `data/streams/micro-cr.md`
- `data/streams/mill-cr.md`
- `data/streams/mormon-cr.md`
- `data/streams/mulberry-r.md`
- `data/streams/mystery-cr.md`
- `data/streams/osage-cr.md`
- `data/streams/pine-cr-ok.md`
- `data/streams/possum-walk-cr.md`
- `data/streams/rattlesnake-cr.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/long-devils-fork-cr.md data/streams/lower-saline-r.md data/streams/m-fork-little-mill-cr.md data/streams/m-fork-little-red-r.md data/streams/meadow-cr.md data/streams/micro-cr.md data/streams/mill-cr.md data/streams/mormon-cr.md data/streams/mulberry-r.md data/streams/mystery-cr.md data/streams/osage-cr.md data/streams/pine-cr-ok.md data/streams/possum-walk-cr.md data/streams/rattlesnake-cr.md
git commit -m "feat: add voice to stream descriptions (batch E: long-devils-rattlesnake)"
```

---

## Task 6: Batch F - Streams richland through spring (14 files)

**Files to Process:**

- `data/streams/richland-cr.md`
- `data/streams/rock-cr.md`
- `data/streams/rockport.md`
- `data/streams/rogers-private-idaho.md`
- `data/streams/saline-r.md`
- `data/streams/salt-fork.md`
- `data/streams/shoal-cr.md`
- `data/streams/shop-cr.md`
- `data/streams/smith-cr.md`
- `data/streams/south-fork-little-red-r.md`
- `data/streams/south-fourche-lafave-r.md`
- `data/streams/spadra-cr.md`
- `data/streams/spirits-cr.md`
- `data/streams/spring-river.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/richland-cr.md data/streams/rock-cr.md data/streams/rockport.md data/streams/rogers-private-idaho.md data/streams/saline-r.md data/streams/salt-fork.md data/streams/shoal-cr.md data/streams/shop-cr.md data/streams/smith-cr.md data/streams/south-fork-little-red-r.md data/streams/south-fourche-lafave-r.md data/streams/spadra-cr.md data/streams/spirits-cr.md data/streams/spring-river.md
git commit -m "feat: add voice to stream descriptions (batch F: richland-spring)"
```

---

## Task 7: Batch G - Streams stepp through wister (14 files)

**Files to Process:**

- `data/streams/stepp-cr.md`
- `data/streams/sugar-cr.md`
- `data/streams/sulphur-cr.md`
- `data/streams/tanyard-cr.md`
- `data/streams/thomas-cr.md`
- `data/streams/trigger-gap.md`
- `data/streams/tulsa-wave.md`
- `data/streams/upper-upper-shoal-cr.md`
- `data/streams/west-fork-white-river.md`
- `data/streams/west-horsehead-cr.md`
- `data/streams/whistlepost-cr.md`
- `data/streams/white-r-middle-fork.md`
- `data/streams/white-rock-cr.md`
- `data/streams/wister-wave.md`

**Step 1-3:** Same process as Task 1

**Step 4: Commit batch**

```bash
git add data/streams/stepp-cr.md data/streams/sugar-cr.md data/streams/sulphur-cr.md data/streams/tanyard-cr.md data/streams/thomas-cr.md data/streams/trigger-gap.md data/streams/tulsa-wave.md data/streams/upper-upper-shoal-cr.md data/streams/west-fork-white-river.md data/streams/west-horsehead-cr.md data/streams/whistlepost-cr.md data/streams/white-r-middle-fork.md data/streams/white-rock-cr.md data/streams/wister-wave.md
git commit -m "feat: add voice to stream descriptions (batch G: stepp-wister)"
```

---

## Task 8: Quality Review

**Step 1: Spot-check sample files**

Read and verify voice quality on:

- `data/streams/big-piney-cr.md` (flagship stream)
- `data/streams/buffalo-r.md` (national river)
- `data/streams/cossatot-r.md` (skull crusher)
- `data/streams/mulberry-r.md` (popular destination)
- `data/streams/richland-cr.md` (wilderness stream)

**Step 2: Check for forbidden patterns**

```bash
grep -l "!" data/streams/*.md | head -5  # Check for exclamation points
grep -il "thrilling\|exciting\|adventure" data/streams/*.md  # Forbidden words
```

Expected: No matches or minimal matches that are appropriate in context.

**Step 3: Verify structure preserved**

```bash
grep -L "## Overview" data/streams/*.md  # All files should have Overview
grep -L "## Sources" data/streams/*.md   # All files should have Sources
```

Expected: No output (all files have required sections)

**Step 4: Final commit if fixes needed**

```bash
git add data/streams/
git commit -m "fix: voice transformation quality fixes"
```

---

## Transformation Voice Reference (Quick Guide)

### Before (dry):

> The creek is characterized by creme de menthe colored water flowing through willow jungles and boulder garden rapids.

### After (voice):

> The water runs that creme de menthe green you only see in the Ozarks. Willow jungles line the banks thick enough to swallow a canoe, and the boulder gardens will keep you honest all the way down.

### Key Phrases to Use:

- "you'll find..." / "you'll want to..."
- "they call it..." / "they named this one..."
- "there's a reason..."
- "make of that what you will"
- "if you know what you're doing" / "if you're paying attention"
- "earned its name" / "earned that reputation"

### Hazards Voice Example:

- Before: "Strainers may be present after storms."
- After: "Strainers show up overnight after storms. They don't announce themselves."

---

## Summary

| Task | Batch | Files | Streams                         |
| ---- | ----- | ----- | ------------------------------- |
| 1    | A     | 12    | adkins through boulder          |
| 2    | B     | 8     | buffalo through eflb            |
| 3    | C     | 13    | fall through hurricane          |
| 4    | D     | 14    | illinois through long-branch    |
| 5    | E     | 14    | long-devils through rattlesnake |
| 6    | F     | 14    | richland through spring         |
| 7    | G     | 14    | stepp through wister            |
| 8    | QA    | -     | Quality review and fixes        |

**Total: 89 files across 7 processing batches + 1 QA task**
