import { Stream } from '../types/stream';

export const determineLevel = (currentReading: number, targetLevels: Stream['targetLevels']) => {
  if (currentReading < targetLevels.tooLow) {
    return 'X'; // Too Low
  } else if (currentReading < targetLevels.optimal) {
    return 'L'; // Low
  } else if (currentReading < targetLevels.high) {
    return 'O'; // Optimal
  } else {
    return 'H'; // High
  }
};

// Removed getLevelColor from here since it's now handled in the component