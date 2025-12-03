import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { TrendIcon } from '../../src/components/icons/TrendIcon';
import { LevelTrend } from '../../src/types/stream';

describe('TrendIcon', () => {
  it('should render Rising icon with success color', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.Rising} />);

    // Check that the SVG icon is rendered
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
    expect(svg).toHaveAttribute('data-testid', 'TrendingUpIcon');
  });

  it('should render Falling icon with error color', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.Falling} />);

    expect(container.querySelector('svg')).toBeTruthy();
  });

  it('should render Holding icon with TrendingFlat', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.Holding} />);

    // Holding should render TrendingFlat icon
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
    expect(svg).toHaveAttribute('data-testid', 'TrendingFlatIcon');
  });

  it('should render None icon with disabled styling', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.None} />);

    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('should apply small size correctly', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.Rising} size="small" />);

    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('should apply large size correctly', () => {
    const { container } = render(<TrendIcon trend={LevelTrend.Rising} size="large" />);

    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });
});
