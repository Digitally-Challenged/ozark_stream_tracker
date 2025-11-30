# Photo Enrichment Plan

## Strategy

**Primary sources (in order):**
1. Wikimedia Commons - `site:commons.wikimedia.org "{stream name}" Arkansas`
2. Flickr Creative Commons - CC-BY, CC-BY-SA licenses
3. Government sources - USGS, NPS (Buffalo River), USFS

**Gap-filling:** Bing Image Search for discovery, then trace to source for license verification.

**Coverage targets:**
- Flagship rivers: 5 images each
- Other streams: Best effort (expect ~70% with 0 images)
- No-image handling: Skip `## Images` section entirely

## Image Format

```markdown
## Images

![Description of image](https://url...)
*Photo: Photographer Name, License, via Source*
```

- Descriptive alt text
- Attribution: photographer, license, source platform
- Use medium sizes (1280px Wikimedia, `_b.jpg` Flickr)
- Images section goes before `## Sources`

## Image Selection Priority

1. Whitewater action shots
2. Scenic river views (bluffs, swimming holes)
3. Put-in/take-out locations
4. Seasonal variety

---

## Tasks

### Batch 1: Flagship Rivers (1-5)

- [ ] Task 1: Buffalo River - 5 images
- [ ] Task 2: Mulberry River - 5 images
- [ ] Task 3: Cossatot River - 5 images
- [ ] Task 4: Kings River - 5 images
- [ ] Task 5: Illinois River - 5 images

### Batch 2: Flagship Rivers (6-10)

- [ ] Task 6: Big Piney Creek - 5 images
- [ ] Task 7: Richland Creek - 5 images
- [ ] Task 8: Spring River - 5 images
- [ ] Task 9: Lee Creek - 5 images
- [ ] Task 10: Little Missouri River - 5 images

### Batch 3: Flagship Rivers (11-15)

- [ ] Task 11: Spadra Creek - 5 images
- [ ] Task 12: South Fourche LaFave - 5 images
- [ ] Task 13: Frog Bayou - 5 images
- [ ] Task 14: West Fork White River - 5 images
- [ ] Task 15: Cadron Creek - 5 images

### Batch 4: Remaining Streams

- [ ] Task 16: Search all remaining ~75 streams, add images where CC-licensed photos found

---

## Verification

After each batch:
- Confirm images load
- Confirm attributions are complete
- Commit changes
