# Phase 2: Stream Image Scraping

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add publicly available images to all 89 stream markdown files with proper attribution.

**Architecture:** Search multiple image sources (Wikimedia Commons, Flickr CC, USGS, NPS, USFS) for each stream. Store image URLs and attribution in markdown files under a new `## Images` section.

**Tech Stack:** WebSearch, WebFetch for image discovery; Markdown for storage

---

## Image Section Format

Add to each stream markdown file:

```markdown
## Images

![{Description}]({image_url})
_Photo: {Photographer}, {License}, via {Source}_

![{Description}]({image_url})
_Photo: {Photographer}, {License}, via {Source}_
```

**Example:**

```markdown
## Images

![Cossatot Falls at high water](https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Cossatot_River_Arkansas.jpg/1280px-Cossatot_River_Arkansas.jpg)
_Photo: Wikimedia Commons contributor, CC BY-SA 4.0, via Wikimedia Commons_

![Paddler running Cossatot Falls](https://live.staticflickr.com/example/12345_abcd1234_b.jpg)
_Photo: Jane Doe, CC BY 2.0, via Flickr_
```

---

## Image Sources (Priority Order)

### 1. Wikimedia Commons (Primary)

- **URL Pattern:** `https://commons.wikimedia.org/wiki/Category:Rivers_of_Arkansas`
- **Search:** `site:commons.wikimedia.org {stream name} Arkansas`
- **License:** Public Domain, CC BY, CC BY-SA
- **Attribution:** Required for CC licenses

### 2. Flickr Creative Commons

- **Search:** `site:flickr.com {stream name} Arkansas kayak OR canoe OR paddling`
- **Filter:** Creative Commons licenses only
- **License:** CC BY, CC BY-SA, CC BY-NC (OK for non-profit)
- **Attribution:** Required

### 3. USGS (Government)

- **Search:** `site:usgs.gov {stream name} Arkansas photo`
- **License:** Public Domain (US Government work)
- **Attribution:** Courtesy, not required

### 4. National Park Service (Buffalo River)

- **Search:** `site:nps.gov buffalo river photo`
- **License:** Public Domain (US Government work)
- **Attribution:** Courtesy

### 5. US Forest Service (Ozark National Forest streams)

- **Search:** `site:fs.usda.gov {stream name} Ozark photo`
- **License:** Public Domain (US Government work)
- **Attribution:** Courtesy

---

## Task 1: High-Priority Streams (15 flagship rivers)

**Streams:** Buffalo River, Mulberry River, Cossatot River, Big Piney Creek, Richland Creek, Kings River, Illinois River, Caddo River, Spring River, Lee Creek, Little Missouri River, Spadra Creek, South Fourche LaFave, Cadron Creek, Frog Bayou

**Files:**

- `data/streams/buffalo-r.md`
- `data/streams/mulberry-r.md`
- `data/streams/cossatot-r.md`
- `data/streams/big-piney-cr.md`
- `data/streams/richland-cr.md`
- `data/streams/kings-river.md`
- `data/streams/illinois-river.md`
- `data/streams/caddo-r.md` (if exists, or `dragover.md`)
- `data/streams/spring-river.md`
- `data/streams/lee-cr.md`
- `data/streams/little-missouri-r.md`
- `data/streams/spadra-cr.md`
- `data/streams/south-fourche-lafave-r.md`
- `data/streams/cadron-cr.md`
- `data/streams/frog-bayou.md`

**Step 1: Search for images**

For each stream, search:

1. `site:commons.wikimedia.org "{stream name}" Arkansas river`
2. `site:flickr.com/photos "{stream name}" Arkansas kayak paddling`
3. `site:nps.gov OR site:usgs.gov "{stream name}" photo`

**Step 2: Validate images**

For each image found:

- Confirm it shows the correct stream (not a different river with similar name)
- Verify license (must be CC or public domain)
- Get direct image URL (not page URL)
- Capture photographer name and license type

**Step 3: Add to markdown**

Append `## Images` section before `## Sources` with:

- 1-3 high-quality images per stream
- Full attribution for each image

**Step 4: Commit batch**

```bash
git add data/streams/buffalo-r.md data/streams/mulberry-r.md data/streams/cossatot-r.md data/streams/big-piney-cr.md data/streams/richland-cr.md data/streams/kings-river.md data/streams/illinois-river.md data/streams/spring-river.md data/streams/lee-cr.md data/streams/little-missouri-r.md data/streams/spadra-cr.md data/streams/south-fourche-lafave-r.md data/streams/cadron-cr.md data/streams/frog-bayou.md
git commit -m "feat: add images to flagship stream files (phase 2, batch 1)"
```

---

## Task 2: Popular Intermediate Streams (20 streams)

**Streams:** Hailstone Creek, Falling Water Creek, Bear Creek, Beech Creek, Hurricane Creek (both), Little Mulberry, Mill Creek, Illinois Bayou, Cedar Creek, Clear Creek, Jack Creek, Sugar Creek, Shoal Creek, Rock Creek, Salt Fork, Blackburn Creek, Hart Creek, Haw Creek, Jordan Creek, Left Hand Prong

**Step 1-4:** Same process as Task 1

**Step 5: Commit batch**

```bash
git add data/streams/hailstone-cr.md data/streams/falling-water-cr.md data/streams/bear-cr.md data/streams/beech-cr.md data/streams/hurricane-cr-franklin.md data/streams/hurricane-cr-newton.md data/streams/little-mulberry-cr.md data/streams/mill-cr.md data/streams/illinois-bayou.md data/streams/cedar-cr.md data/streams/clear-cr.md data/streams/jack-cr.md data/streams/sugar-cr.md data/streams/shoal-cr.md data/streams/rock-cr.md data/streams/salt-fork.md data/streams/blackburn-cr.md data/streams/hart-cr.md data/streams/haw-cr.md data/streams/jordan-cr.md data/streams/left-hand-prong.md
git commit -m "feat: add images to intermediate stream files (phase 2, batch 2)"
```

---

## Task 3: Expert Creeks (20 streams)

**Streams:** Adkins Creek, Ben Doodle Creek, Big Devils Fork, Bobtail Creek, Boss Hollow, Boulder Creek, EFLB, Ellis Creek, Falls Branch, Fern Gulley, Long Devils Fork, Mormon Creek, Mystery Creek, Osage Creek, Possum Walk Creek, Rattlesnake Creek, Shop Creek, Smith Creek, Stepp Creek, Sulphur Creek

**Note:** Expert creeks often have fewer public images. May find 0-1 images for some.

**Step 1-4:** Same process as Task 1

**Step 5: Commit batch**

```bash
git add data/streams/adkins-cr.md data/streams/ben-doodle-cr.md data/streams/big-devils-fork-cr.md data/streams/bobtail-cr.md data/streams/boss-hollow.md data/streams/boulder-cr.md data/streams/eflb.md data/streams/ellis-cr.md data/streams/falls-br.md data/streams/fern-gulley.md data/streams/long-devils-fork-cr.md data/streams/mormon-cr.md data/streams/mystery-cr.md data/streams/osage-cr.md data/streams/possum-walk-cr.md data/streams/rattlesnake-cr.md data/streams/shop-cr.md data/streams/smith-cr.md data/streams/stepp-cr.md data/streams/sulphur-cr.md
git commit -m "feat: add images to expert creek files (phase 2, batch 3)"
```

---

## Task 4: Remaining Streams (34 streams)

**All remaining streams not covered in Tasks 1-3**

**Step 1-4:** Same process as Task 1

**Step 5: Commit batch**

```bash
git add data/streams/*.md
git commit -m "feat: add images to remaining stream files (phase 2, batch 4)"
```

---

## Task 5: Quality Review

**Step 1: Check all files have Images section or explicit "no images found"**

```bash
grep -L "## Images" data/streams/*.md | grep -v "_"
```

For files without images, add:

```markdown
## Images

_No publicly available images found. If you have photos of this creek, consider contributing to Wikimedia Commons._
```

**Step 2: Verify all attributions are complete**

```bash
grep -A2 "## Images" data/streams/*.md | grep -v "Photo:"
```

Should only show image URLs and blank lines, not missing attributions.

**Step 3: Test a few image URLs**

Manually verify 5-10 random image URLs still load correctly.

**Step 4: Final commit**

```bash
git add data/streams/
git commit -m "fix: complete image section for all streams (phase 2 complete)"
```

---

## Image Search Tips

### Wikimedia Commons Direct URLs

When you find an image on Commons, get the direct file URL:

- Page: `https://commons.wikimedia.org/wiki/File:Cossatot_River.jpg`
- Direct: `https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Cossatot_River.jpg/1280px-Cossatot_River.jpg`

Use `/1280px-` prefix for reasonable size.

### Flickr Direct URLs

For Flickr, use the static URL format:

- Page: `https://www.flickr.com/photos/user/12345678`
- Direct: `https://live.staticflickr.com/server/id_secret_b.jpg`

Use `_b.jpg` suffix for large size (1024px).

### Search Query Variations

Try multiple name formats:

- "Cossatot River"
- "Cossatot Falls"
- "Cossatot Creek"
- "Cossatot Arkansas"
- "Cossatot kayak"
- "Cossatot whitewater"

---

## Summary

| Task | Batch        | Streams | Priority                                      |
| ---- | ------------ | ------- | --------------------------------------------- |
| 1    | Flagship     | 15      | High - popular rivers with many images        |
| 2    | Intermediate | 20      | Medium - well-known creeks                    |
| 3    | Expert       | 20      | Lower - obscure creeks, fewer images expected |
| 4    | Remaining    | 34      | Complete coverage                             |
| 5    | QA           | All     | Verify completeness                           |

**Expected outcome:** 89 streams with image sections. Flagship streams: 2-3 images each. Obscure creeks: 0-1 images with placeholder text.
