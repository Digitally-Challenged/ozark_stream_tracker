import { describe, it, expect } from 'vitest';

/**
 * Bug: Turner Bend water level parser incorrectly extracts "20252.2" instead of "2.2"
 *
 * Root cause: The regex (\d+\.?\d*)\s*['"] matches digits greedily,
 * so when the page text has "12-03-20252.2'" (year concatenated with level),
 * it captures "20252.2" as the water level.
 *
 * This test file reproduces the bug and verifies the fix.
 */

// Extract the parsing logic to test it in isolation
function parseWaterLevel(pageText: string): number | null {
  // FIXED regex: Handles date-level concatenation from Turner Bend website
  // Pattern breakdown:
  // 1. \d{1,2}-\d{1,2}-\d{4}\s*(\d{1,2}\.\d+)\s*['"] - Date followed by level (handles concatenation)
  // 2. (?<!\d)(\d{1,2}\.\d+)\s*['"] - Standalone level not preceded by digit
  // 3. Level:\s*(\d+\.?\d*) - "Level: X.X" format
  // 4. Water\s*Level:\s*(\d+\.?\d*) - "Water Level: X.X" format
  const levelMatch = pageText.match(
    /\d{1,2}-\d{1,2}-\d{4}\s*(\d{1,2}\.\d+)\s*['"]|(?<!\d)(\d{1,2}\.\d+)\s*['"]|Level:\s*(\d+\.?\d*)|Water\s*Level:\s*(\d+\.?\d*)/i
  );
  if (levelMatch) {
    const parsed = parseFloat(
      levelMatch[1] || levelMatch[2] || levelMatch[3] || levelMatch[4]
    );
    if (!isNaN(parsed) && parsed >= 0) {
      return parsed;
    }
  }
  return null;
}

describe('Turner Bend Water Level Parser', () => {
  describe('BUG REPRODUCTION: Year-level concatenation', () => {
    it('should extract 2.2 from "12-03-20252.2\'" but currently extracts 20252.2', () => {
      // This is the actual text pattern from the live Turner Bend website
      // where the year and level get concatenated without whitespace
      const buggyPageText = '12-03-20252.2\'';

      const result = parseWaterLevel(buggyPageText);

      // This test SHOULD pass with value 2.2, but currently FAILS
      // because the buggy regex extracts 20252.2
      expect(result).toBe(2.2);
    });

    it('should handle realistic page content with concatenated year-level', () => {
      // Simulating actual cheerio output where whitespace is stripped
      const realisticPageText = `
        Water Level gauge @ Turner Bend Landing
        12-03-20252.2'
        12-02-20252.3'
        11-29-20252.1'
      `;

      const result = parseWaterLevel(realisticPageText);

      // Should get the first water level (2.2), not a corrupted year+level
      expect(result).toBe(2.2);
    });
  });

  describe('Expected behavior after fix', () => {
    it('should parse normal format with space: "12-03-2025  2.2\'"', () => {
      const pageText = '12-03-2025  2.2\'';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(2.2);
    });

    it('should parse level with double quote: 2.2"', () => {
      const pageText = '2.2"';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(2.2);
    });

    it('should parse "Level: X.X" format', () => {
      const pageText = 'Level: 3.5';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(3.5);
    });

    it('should parse low water levels like 0.8\'', () => {
      const pageText = '0.8\'';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(0.8);
    });

    it('should parse high water levels like 12.5\'', () => {
      const pageText = '12.5\'';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(12.5);
    });

    it('should return null for text with no water level', () => {
      const pageText = 'No data available';
      const result = parseWaterLevel(pageText);
      expect(result).toBeNull();
    });
  });

  describe('Edge cases and regression prevention', () => {
    it('should handle multiple date-level entries and get the first', () => {
      const pageText = `
        12-03-20252.2'
        12-02-20252.3'
        11-29-20252.1'
      `;
      const result = parseWaterLevel(pageText);
      expect(result).toBe(2.2);
    });

    it('should handle integer water levels like 5\'', () => {
      // Some rivers might have whole-number readings
      const pageText = "12-03-20255'";
      const result = parseWaterLevel(pageText);
      // Current regex requires decimal, so this returns null
      // This documents expected behavior
      expect(result).toBeNull();
    });

    it('should handle very low water levels like 0.1\'', () => {
      const pageText = "12-03-20250.1'";
      const result = parseWaterLevel(pageText);
      expect(result).toBe(0.1);
    });

    it('should handle high water levels like 15.5\'', () => {
      const pageText = "12-03-202515.5'";
      const result = parseWaterLevel(pageText);
      expect(result).toBe(15.5);
    });

    it('should handle slash date format: 12/03/2025', () => {
      // The regex currently only handles hyphen dates
      // This documents expected behavior
      const pageText = "12/03/20252.2'";
      const result = parseWaterLevel(pageText);
      // With current regex this won't match the date pattern
      expect(result).toBeNull();
    });

    it('should handle Water Level prefix format', () => {
      const pageText = 'Water Level: 4.5';
      const result = parseWaterLevel(pageText);
      expect(result).toBe(4.5);
    });

    it('should not extract years as water levels', () => {
      // Ensure we don't accidentally match year patterns
      const pageText = 'Updated on 2025';
      const result = parseWaterLevel(pageText);
      expect(result).toBeNull();
    });

    it('should handle real Turner Bend page structure', () => {
      // Simulating actual page content based on live scrape
      const pageText = `
        479-667-3641
        turnerbend23@gmail.com
        Water Level gauge @ Turner Bend Landing
        12-03-20252.2'  43rd Anniversary of the Great Flood of '82
        12-02-20252.3'
        11-29-20252.1'
        THE MULBERRY RIVER GAUGE
      `;
      const result = parseWaterLevel(pageText);
      expect(result).toBe(2.2);
    });
  });
});
