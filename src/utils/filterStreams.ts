import { StreamData } from '../types/stream';

export function filterByRatingAndSize(
  streams: StreamData[],
  selectedRatings: string[],
  selectedSizes: string[]
): StreamData[] {
  return streams.filter((stream) => {
    if (
      selectedRatings.length > 0 &&
      !selectedRatings.includes(stream.rating)
    ) {
      return false;
    }
    if (selectedSizes.length > 0 && !selectedSizes.includes(stream.size)) {
      return false;
    }
    return true;
  });
}
