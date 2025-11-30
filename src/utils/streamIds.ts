import { getAllStreamIds } from '../data/streamContent.generated';

// Map stream names to their markdown file IDs
const streamNameToIdMap: Record<string, string> = {};

// Build the map on module load
const allIds = getAllStreamIds();
for (const id of allIds) {
  // Create variations of the ID for matching
  const normalized = id.toLowerCase().replace(/-/g, ' ');
  streamNameToIdMap[normalized] = id;
}

/**
 * Convert a stream name to its corresponding markdown file ID
 * e.g., "Buffalo National River" -> "buffalo-r"
 */
export function getStreamIdFromName(name: string): string | null {
  // First try direct lookup by normalized name
  const normalized = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();

  // Try exact match with ID variations
  for (const id of allIds) {
    const idNormalized = id.toLowerCase().replace(/-/g, ' ');
    if (
      normalized === idNormalized ||
      normalized.includes(idNormalized) ||
      idNormalized.includes(normalized)
    ) {
      return id;
    }
  }

  // Try matching by first word (common for rivers like "Buffalo" -> "buffalo-r")
  const firstWord = normalized.split(' ')[0];
  for (const id of allIds) {
    if (id.toLowerCase().startsWith(firstWord)) {
      return id;
    }
  }

  return null;
}
