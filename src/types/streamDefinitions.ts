// types/streamDefinitions.ts

/** Detailed size category definitions */
export const sizeDefinitions = {
  XS: {
    name: 'Extra Small',
    width: '< 20ft',
    watershed: '< 1 sq mi',
    rainRate: '1.5 in/hr',
    window: '3-6 hrs',
    description: 'Extra small creeks with very quick response to rain'
  },
  VS: {
    name: 'Very Small',
    width: '20-30ft',
    watershed: '1-4 sq mi',
    rainRate: '1.0 in/hr',
    window: '6-12 hrs',
    description: 'Very small creeks with quick response to rain'
  },
  S: {
    name: 'Small',
    width: '30-40ft',
    watershed: '4-10 sq mi',
    rainRate: '0.75 in/hr',
    window: '1 day',
    description: 'Small creeks with moderate response time'
  },
  M: {
    name: 'Medium',
    width: '40-75ft',
    watershed: '10-25 sq mi',
    rainRate: '0.5 in/hr',
    window: '1-2 days',
    description: 'Medium sized streams with longer response time'
  },
  L: {
    name: 'Large',
    width: '> 75ft',
    watershed: '> 25 sq mi',
    rainRate: '0.2 in/hr',
    window: '2-5 days',
    description: 'Large rivers with extended response time'
  },
  H: {
    name: 'Huge',
    width: '> 150ft',
    watershed: '> 75 sq mi',
    rainRate: '0.1 in/hr',
    window: '5+ days',
    description: 'Major rivers with very long response time'
  },
  DC: {
    name: 'Dam Controlled',
    width: 'N/A',
    watershed: 'N/A',
    rainRate: 'N/A',
    window: 'Scheduled',
    description: 'Flow controlled by dam releases - check schedule'
  },
  A: {
    name: 'Always Runs',
    width: 'N/A',
    watershed: 'N/A',
    rainRate: 'N/A',
    window: 'N/A',
    description: 'Consistent flow year-round'
  }
} as const;

/** Detailed correlation quality definitions */
export const correlationDefinitions = {
  'A': {
    name: 'Excellent',
    description: 'Excellent correlation. Gauge is on the creek near the run'
  },
  'A+': {
    name: 'Excellent Plus',
    description: 'Gauge is on a small creek and should be rising for a good run'
  },
  'B': {
    name: 'Good',
    description: 'Good correlation. Creek is an upstream tributary to the gauged creek'
  },
  'B+': {
    name: 'Good Plus',
    description: 'Creek is a small upstream tributary to the gauged creek. Gauge should be rising'
  },
  'C': {
    name: 'Fair',
    description: 'Fair correlation. Creek is in a nearby watershed or downstream tributary'
  },
  'C+': {
    name: 'Fair Plus',
    description: 'Same as Fair, but creek is small and gauge should be rising'
  },
  'D': {
    name: 'Poor',
    description: 'Poor correlation. Creek is weakly correlated to the gauge'
  },
  'D+': {
    name: 'Poor Plus',
    description: 'Same as Poor, but creek is small and gauge should be rising'
  },
  'F': {
    name: 'Unknown',
    description: 'No/Unknown correlation. Wild guess at best'
  }
} as const;

/** Water level condition definitions */
export const levelDefinitions = {
  tooLow: {
    name: 'Too Low',
    code: 'X',
    color: '#FF0000',
    description: 'Creek is too low for fun paddling'
  },
  low: {
    name: 'Low',
    code: 'L',
    color: '#FFFF00',
    description: 'Creek is low but paddlable. May have to drag/portage in places'
  },
  optimal: {
    name: 'Optimal',
    code: 'O',
    color: '#00FF00',
    description: 'Creek is perfect for paddling. The ratings listed are for this range'
  },
  high: {
    name: 'High/Flood',
    code: 'H',
    color: '#0000FF',
    description: 'Creek is high and potentially very dangerous. Many more hazards are present in this range'
  }
} as const;

/** Type-safe helpers to get definitions */
export function getSizeDefinition(size: keyof typeof sizeDefinitions) {
  return sizeDefinitions[size];
}

export function getCorrelationDefinition(quality: keyof typeof correlationDefinitions) {
  return correlationDefinitions[quality];
}

export function getLevelDefinition(level: keyof typeof levelDefinitions) {
  return levelDefinitions[level];
}