// src/components/dashboard/DashboardSidebar.tsx
import {
  Box,
  Drawer,
  IconButton,
  // List, // Not strictly needed if using FormControl/FormGroup directly for sections
  // ListItem,
  ListItemText, // Still useful within Select MenuItem
  Divider,
  useTheme,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  OutlinedInput, // Added for Select if needed for label
} from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select'; // For typing Select onChange
import { Close } from '@mui/icons-material';

interface DashboardSidebarProps {
  open: boolean;
  onClose: () => void;
  width?: number;
  selectedRatings: string[];
  setSelectedRatings: (
    ratings: string[] | ((prevRatings: string[]) => string[])
  ) => void; // Allow functional updates
  selectedSizes: string[];
  setSelectedSizes: (
    sizes: string[] | ((prevSizes: string[]) => string[])
  ) => void; // Allow functional updates
}

export function DashboardSidebar({
  open = false,
  onClose,
  width = 320,
  selectedRatings,
  setSelectedRatings,
  selectedSizes,
  setSelectedSizes,
}: DashboardSidebarProps) {
  const theme = useTheme();

  const ratings = [
    'I',
    'II',
    'III',
    'IV',
    'V',
    'II-III',
    'III-IV',
    'A',
    'PLAY',
  ]; // Added A and PLAY as they are in data
  const sizes = ['XS', 'VS', 'S', 'M', 'L', 'H', 'DC', 'A']; // Added H, DC, A as they are in data

  const handleRatingChange = (event: SelectChangeEvent<string[]>) => {
    const {
      target: { value },
    } = event;
    setSelectedRatings(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value
    );
  };

  const handleSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setSelectedSizes((prevSizes) =>
      checked ? [...prevSizes, name] : prevSizes.filter((s) => s !== name)
    );
  };

  const content = (
    <Box
      sx={{
        height: '100%',
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        display: 'flex',
        flexDirection: 'column',
        p: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}
      >
        <Typography variant="h6" component="div">
          Filters
        </Typography>
        <IconButton
          onClick={onClose}
          sx={{ color: theme.palette.text.primary }}
        >
          <Close />
        </IconButton>
      </Box>

      <Divider sx={{ mb: 2, borderColor: theme.palette.divider }} />

      {/* Filter by Rating */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="rating-select-label">Rating</InputLabel>
        <Select
          labelId="rating-select-label"
          id="rating-select"
          multiple
          value={selectedRatings} // Used prop
          onChange={handleRatingChange} // Used handler
          input={<OutlinedInput label="Rating" />} // Ensures label floats correctly
          renderValue={(selected) => selected.join(', ')}
          MenuProps={{
            // Prevents menu from overlapping the select input too much
            PaperProps: {
              style: {
                maxHeight: 224, // Example max height
              },
            },
          }}
        >
          {ratings.map((rating) => (
            <MenuItem key={rating} value={rating}>
              <Checkbox checked={selectedRatings.indexOf(rating) > -1} />{' '}
              {/* Reflects selection */}
              <ListItemText primary={rating} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Divider sx={{ mb: 2, borderColor: theme.palette.divider }} />

      {/* Filter by Size */}
      <Typography
        variant="subtitle1"
        gutterBottom
        component="div"
        sx={{ mt: 1 }}
      >
        {' '}
        {/* Added mt for spacing */}
        Size
      </Typography>
      <FormGroup sx={{ mb: 2 }}>
        {sizes.map((size) => (
          <FormControlLabel
            key={size}
            control={
              <Checkbox
                checked={selectedSizes.indexOf(size) > -1} // Reflects selection
                onChange={handleSizeChange} // Used handler
                name={size}
              />
            }
            label={size}
          />
        ))}
      </FormGroup>
    </Box>
  );

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      variant="temporary"
      elevation={4}
      sx={{
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
          backgroundColor: theme.palette.background.default,
          border: 'none',
        },
      }}
    >
      {content}
    </Drawer>
  );
}
