export const STREAM_METADATA = {
  sizeDefinitions: {
    XS: {
      width: '< 20ft',
      watershed: '< 1 sq mi',
      rainRate: '1.5 in/hr',
      window: '3-6 hrs',
    },
    VS: {
      width: '20-30ft',
      watershed: '1-4 sq mi',
      rainRate: '1.0 in/hr',
      window: '6-12 hrs',
    },
    S: {
      width: '30-40ft',
      watershed: '4-10 sq mi',
      rainRate: '0.75 in/hr',
      window: '1 day',
    },
    M: {
      width: '40-75ft',
      watershed: '10-25 sq mi',
      rainRate: '0.5 in/hr',
      window: '1-2 days',
    },
    L: {
      width: '> 75ft',
      watershed: '> 25 sq mi',
      rainRate: '0.2 in/hr',
      window: '2-5 days',
    },
    H: {
      width: '> 150ft',
      watershed: '> 75 sq mi',
      rainRate: '0.1 in/hr',
      window: '5+ days',
    },
    DC: {
      width: 'N/A',
      watershed: 'N/A',
      rainRate: 'N/A',
      window: 'Dam Controlled - Check Schedule!',
    },
    A: {
      width: 'N/A',
      watershed: 'N/A',
      rainRate: 'N/A',
      window: 'Always Runs',
    },
  },
  correlationQualityDefinitions: {
    A: 'Excellent correlation. Gauge is on the creek near the run',
    'A+': 'Gauge is on a small creek and should be rising for a good run',
    B: 'Good correlation. Creek is an upstream tributary to the gauged creek',
    'B+': 'Creek is a small upstream tributary to the gauged creek. Gauge should be rising',
    C: 'Fair correlation. Creek is in a nearby watershed or downstream tributary',
    'C+': 'Same as C, but creek is small and gauge should be rising',
    D: 'Poor correlation. Creek is weakly correlated to the gauge',
    'D+': 'Same as D, but creek is small and gauge should be rising',
    F: 'No/Unknown correlation. Wild guess at best',
  },
  levelDefinitions: {
    tooLow: {
      code: 'X',
      color: '#FF0000',
      description: 'Creek is too low for fun paddling',
    },
    low: {
      code: 'L',
      color: '#FFFF00',
      description:
        'Creek is low but paddlable. May have to drag/portage in places',
    },
    optimal: {
      code: 'O',
      color: '#00FF00',
      description:
        'Creek is perfect for paddling. The ratings listed are for this range',
    },
    high: {
      code: 'H',
      color: '#0000FF',
      description:
        'Creek is high and potentially very dangerous. Many more hazards are present',
    },
  },
};
