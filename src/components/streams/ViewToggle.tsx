// src/components/streams/ViewToggle.tsx
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import { ViewList, ViewModule } from '@mui/icons-material';
import { ViewMode } from '../../hooks/useViewPreference';

interface ViewToggleProps {
  viewMode: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function ViewToggle({ viewMode, onChange }: ViewToggleProps) {
  const handleChange = (
    _: React.MouseEvent<HTMLElement>,
    newMode: ViewMode | null
  ) => {
    if (newMode !== null) {
      onChange(newMode);
    }
  };

  return (
    <ToggleButtonGroup
      value={viewMode}
      exclusive
      onChange={handleChange}
      size="small"
      aria-label="view mode"
    >
      <ToggleButton value="table" aria-label="table view">
        <Tooltip title="Table View">
          <ViewList />
        </Tooltip>
      </ToggleButton>
      <ToggleButton value="cards" aria-label="card view">
        <Tooltip title="Card View">
          <ViewModule />
        </Tooltip>
      </ToggleButton>
    </ToggleButtonGroup>
  );
}
