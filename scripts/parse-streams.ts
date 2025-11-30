/**
 * Parse stream markdown files and generate TypeScript data
 * Run with: npx tsx scripts/parse-streams.ts
 */

import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import type {
  StreamContent,
  StreamSection,
  AccessPoint,
  StreamImage,
  StreamSource,
  StreamOverview,
} from '../src/types/streamContent.js';

const STREAMS_DIR = path.join(process.cwd(), 'data/streams');
const OUTPUT_FILE = path.join(
  process.cwd(),
  'src/data/streamContent.generated.ts'
);

function parseOverview(content: string): StreamOverview {
  const overview: StreamOverview = {
    rating: '',
    watershedSize: '',
    gradient: '',
    length: '',
    season: '',
  };

  const overviewMatch = content.match(/## Overview\n([\s\S]*?)(?=\n## |$)/);
  if (overviewMatch) {
    const overviewText = overviewMatch[1];
    const ratingMatch = overviewText.match(/\*\*Rating:\*\*\s*(.+)/);
    const sizeMatch = overviewText.match(/\*\*Watershed Size:\*\*\s*(.+)/);
    const gradientMatch = overviewText.match(/\*\*Gradient:\*\*\s*(.+)/);
    const lengthMatch = overviewText.match(/\*\*Length:\*\*\s*(.+)/);
    const seasonMatch = overviewText.match(/\*\*Season:\*\*\s*(.+)/);

    if (ratingMatch) overview.rating = ratingMatch[1].trim();
    if (sizeMatch) overview.watershedSize = sizeMatch[1].trim();
    if (gradientMatch) overview.gradient = gradientMatch[1].trim();
    if (lengthMatch) overview.length = lengthMatch[1].trim();
    if (seasonMatch) overview.season = seasonMatch[1].trim();
  }

  return overview;
}

function parseDescription(content: string): string {
  const descMatch = content.match(/## Description\n([\s\S]*?)(?=\n## |$)/);
  return descMatch ? descMatch[1].trim() : '';
}

function parseSections(content: string): StreamSection[] {
  const sections: StreamSection[] = [];
  const sectionsMatch = content.match(/## Sections\n([\s\S]*?)(?=\n## |$)/);

  if (sectionsMatch) {
    const sectionsText = sectionsMatch[1];
    const sectionBlocks = sectionsText.split(/\n### /).slice(1);

    for (const block of sectionBlocks) {
      const lines = block.split('\n');
      const name = lines[0].trim();
      const section: StreamSection = { name };

      for (const line of lines.slice(1)) {
        const distMatch = line.match(/\*\*Distance:\*\*\s*(.+)/);
        const ratingMatch = line.match(/\*\*Rating:\*\*\s*(.+)/);
        const gradientMatch = line.match(/\*\*Gradient:\*\*\s*(.+)/);
        const charMatch = line.match(/\*\*Character:\*\*\s*(.+)/);
        const notesMatch = line.match(/\*\*Notes:\*\*\s*(.+)/);

        if (distMatch) section.distance = distMatch[1].trim();
        if (ratingMatch) section.rating = ratingMatch[1].trim();
        if (gradientMatch) section.gradient = gradientMatch[1].trim();
        if (charMatch) section.character = charMatch[1].trim();
        if (notesMatch) section.notes = notesMatch[1].trim();
      }

      sections.push(section);
    }
  }

  return sections;
}

function parseAccessPoints(content: string): AccessPoint[] {
  const accessPoints: AccessPoint[] = [];
  const accessMatch = content.match(/## Access Points\n([\s\S]*?)(?=\n## |$)/);

  if (accessMatch) {
    const accessText = accessMatch[1];
    const pointBlocks = accessText.split(/\n### /).slice(1);

    for (const block of pointBlocks) {
      const lines = block.split('\n');
      const name = lines[0].trim();
      const point: AccessPoint = { name };

      for (const line of lines.slice(1)) {
        const locMatch = line.match(/\*\*Location:\*\*\s*(.+)/);
        const dirMatch = line.match(/\*\*Directions:\*\*\s*(.+)/);
        const notesMatch = line.match(/\*\*Notes:\*\*\s*(.+)/);

        if (locMatch) point.location = locMatch[1].trim();
        if (dirMatch) point.directions = dirMatch[1].trim();
        if (notesMatch) point.notes = notesMatch[1].trim();
      }

      accessPoints.push(point);
    }
  }

  return accessPoints;
}

function parseHazards(content: string): string[] {
  const hazards: string[] = [];
  const hazardsMatch = content.match(/## Hazards\n([\s\S]*?)(?=\n## |$)/);

  if (hazardsMatch) {
    const lines = hazardsMatch[1].split('\n');
    for (const line of lines) {
      const itemMatch = line.match(/^-\s+(.+)/);
      if (itemMatch) {
        hazards.push(itemMatch[1].trim());
      }
    }
  }

  return hazards;
}

function parseRapids(content: string): string[] {
  const rapids: string[] = [];
  const rapidsMatch = content.match(
    /## Rapids & Features\n([\s\S]*?)(?=\n## |$)/
  );

  if (rapidsMatch) {
    const lines = rapidsMatch[1].split('\n');
    for (const line of lines) {
      const itemMatch = line.match(/^-\s+\*\*(.+?)\*\*/);
      if (itemMatch) {
        rapids.push(itemMatch[1].trim());
      }
    }
  }

  return rapids;
}

function parseImages(content: string): StreamImage[] {
  const images: StreamImage[] = [];
  const imagesMatch = content.match(/## Images\n([\s\S]*?)(?=\n## |$)/);

  if (imagesMatch) {
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)\n\*([^*]+)\*/g;
    let match;

    while ((match = imageRegex.exec(imagesMatch[1])) !== null) {
      images.push({
        alt: match[1],
        url: match[2],
        caption: match[3].trim(),
      });
    }
  }

  return images;
}

function parseSources(content: string): StreamSource[] {
  const sources: StreamSource[] = [];
  const sourcesMatch = content.match(/## Sources\n([\s\S]*?)$/);

  if (sourcesMatch) {
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;

    while ((match = linkRegex.exec(sourcesMatch[1])) !== null) {
      sources.push({
        title: match[1],
        url: match[2],
      });
    }
  }

  return sources;
}

function parseGeographicContext(content: string): string {
  const match = content.match(/## Geographic Context\n([\s\S]*?)(?=\n## |$)/);
  return match ? match[1].trim() : '';
}

function parseSpecialDesignation(content: string): string {
  const match = content.match(/## Special Designation\n([\s\S]*?)(?=\n## |$)/);
  return match ? match[1].trim() : '';
}

function parseStreamFile(filePath: string): StreamContent | null {
  const fileName = path.basename(filePath, '.md');

  // Skip template and voice prompt files
  if (fileName.startsWith('_')) {
    return null;
  }

  const fileContent = fs.readFileSync(filePath, 'utf-8');
  const { content } = matter(fileContent);

  // Extract name from first H1
  const nameMatch = content.match(/^# (.+)/m);
  const name = nameMatch ? nameMatch[1].trim() : fileName;

  return {
    id: fileName,
    name,
    overview: parseOverview(content),
    description: parseDescription(content),
    sections: parseSections(content),
    accessPoints: parseAccessPoints(content),
    rapids: parseRapids(content),
    hazards: parseHazards(content),
    tributaries: [],
    images: parseImages(content),
    sources: parseSources(content),
    geographicContext: parseGeographicContext(content),
    specialDesignation: parseSpecialDesignation(content),
  };
}

function main() {
  console.log('Parsing stream markdown files...');

  const files = fs.readdirSync(STREAMS_DIR).filter((f) => f.endsWith('.md'));
  const streams: Record<string, StreamContent> = {};

  for (const file of files) {
    const filePath = path.join(STREAMS_DIR, file);
    const stream = parseStreamFile(filePath);

    if (stream) {
      streams[stream.id] = stream;
      console.log(`  Parsed: ${stream.name}`);
    }
  }

  const output = `// AUTO-GENERATED FILE - DO NOT EDIT
// Generated by: npx tsx scripts/parse-streams.ts

import type { StreamContentMap } from '../types/streamContent';

export const streamContent: StreamContentMap = ${JSON.stringify(streams, null, 2)};

export function getStreamContent(id: string) {
  return streamContent[id] || null;
}

export function getAllStreamIds(): string[] {
  return Object.keys(streamContent);
}
`;

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(OUTPUT_FILE, output);
  console.log(`\nGenerated: ${OUTPUT_FILE}`);
  console.log(`Total streams: ${Object.keys(streams).length}`);
}

main();
