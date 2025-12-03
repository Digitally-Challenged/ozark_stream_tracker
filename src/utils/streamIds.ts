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
  Rockport: 'rockport',
  "Roger's Private Idaho": 'rogers-private-idaho',
  'Caddo R.': 'caddo-r',
  'Camp Cr.': 'camp-cr',
  'Dragover (Ouachita R.)': 'dragover',
  'Ellis Cr.': 'ellis-cr',
  'Saint Francis R. (MO)': 'saint-francis-r',
  'WOKA Whitewater Park': 'woka-whitewater-park',

  // EFLB special case
  EFLB: 'eflb',
};

// Validate mappings on module load (development only)
if (import.meta.env.DEV) {
  const allIds = new Set(getAllStreamIds());
  for (const [name, id] of Object.entries(STREAM_NAME_TO_ID)) {
    if (!allIds.has(id)) {
      console.warn(
        `[streamIds] Invalid mapping: "${name}" -> "${id}" (content ID not found)`
      );
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
