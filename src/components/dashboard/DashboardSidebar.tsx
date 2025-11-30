import {
  Box,
  Drawer,
  IconButton,
  ListItemText,
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
  OutlinedInput,
  Button,
} from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select';
import { Close, FilterAltOff } from '@mui/icons-material';
import { UI_CONFIG } from '../../constants';

interface DashboardSidebarProps {
  open: boolean;
  onClose: () => void;
  width?: number;
  selectedRatings: string[];
  setSelectedRatings: (
    ratings: string[] | ((prevRatings: string[]) => string[])
  ) => void;
  selectedSizes: string[];
  setSelectedSizes: (
    sizes: string[] | ((prevSizes: string[]) => string[])
  ) => void;
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
    'A',
    'I-II',
    'I-II+',
    'I-III',
    'II',
    'II+',
    'II+-III',
    'II-III',
    'II-III+',
    'II-IV',
    'III',
    'III+',
    'III-IV',
    'III-IV+',
    'III-IV (V)',
    'III-V',
    'IV (IV+)',
    'IV (V)',
    'IV+',
    'IV+ (V)',
    'IV-V',
    'IV-V+',
    'IV-V (P)',
    'IV-V+ (P)',
    'PLAY',
  ];
  const sizes = ['XS', 'VS', 'S', 'M', 'L', 'H', 'DC', 'A'];

  const handleRatingChange = (event: SelectChangeEvent<string[]>) => {
    const {
      target: { value },
    } = event;
    setSelectedRatings(typeof value === 'string' ? value.split(',') : value);
  };

  const handleSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setSelectedSizes((prevSizes) =>
      checked ? [...prevSizes, name] : prevSizes.filter((s) => s !== name)
    );
  };

  const handleClearFilters = () => {
    setSelectedRatings([]);
    setSelectedSizes([]);
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

      <Button
        variant="outlined"
        fullWidth
        startIcon={<FilterAltOff />}
        onClick={handleClearFilters}
        disabled={selectedRatings.length === 0 && selectedSizes.length === 0}
        sx={{ mb: 2 }}
      >
        Clear Filters
      </Button>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="rating-select-label">Rating</InputLabel>
        <Select
          labelId="rating-select-label"
          id="rating-select"
          multiple
          value={selectedRatings}
          onChange={handleRatingChange}
          input={<OutlinedInput label="Rating" />}
          renderValue={(selected) => selected.join(', ')}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: UI_CONFIG.SIDEBAR_FILTER_MAX_HEIGHT,
              },
            },
          }}
        >
          {ratings.map((rating) => (
            <MenuItem key={rating} value={rating}>
              <Checkbox checked={selectedRatings.indexOf(rating) > -1} />
              <ListItemText primary={rating} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Divider sx={{ mb: 2, borderColor: theme.palette.divider }} />

      <Typography
        variant="subtitle1"
        gutterBottom
        component="div"
        sx={{ mt: 1 }}
      >
        Size
      </Typography>
      <FormGroup sx={{ mb: 2 }}>
        {sizes.map((size) => (
          <FormControlLabel
            key={size}
            control={
              <Checkbox
                checked={selectedSizes.indexOf(size) > -1}
                onChange={handleSizeChange}
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
