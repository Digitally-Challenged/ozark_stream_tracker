import { Stream } from '../types/stream';

export const determineLevel = (currentReading: number, targetLevels: Stream['targetLevels']) => {
  if (currentReading < targetLevels.tooLow) {
    return 'Too Low'; // Too Low
  } else if (currentReading < targetLevels.optimal) {
    return 'Low'; // Low
  } else if (currentReading < targetLevels.high) {
    return 'Optimal'; // Optimal
  } else {
    return 'High/Flood'; // High
  }
};

// Removed getLevelColor from here since it's now handled in the component