// Types for parsed stream markdown content

export interface StreamOverview {
  rating: string;
  watershedSize: string;
  gradient: string;
  length: string;
  season: string;
}

export interface StreamSection {
  name: string;
  distance?: string;
  rating?: string;
  gradient?: string;
  character?: string;
  features?: string[];
  notes?: string;
}

export interface AccessPoint {
  name: string;
  location?: string;
  directions?: string;
  notes?: string;
}

export interface StreamImage {
  url: string;
  alt: string;
  caption: string;
}

export interface StreamSource {
  title: string;
  url: string;
}

export interface StreamContent {
  id: string;
  name: string;
  overview: StreamOverview;
  description: string;
  sections: StreamSection[];
  accessPoints: AccessPoint[];
  rapids: string[];
  hazards: string[];
  tributaries: string[];
  images: StreamImage[];
  sources: StreamSource[];
  specialDesignation?: string;
  geographicContext?: string;
}

// Map of stream ID to content
export type StreamContentMap = Record<string, StreamContent>;
