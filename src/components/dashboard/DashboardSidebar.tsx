import {
  Box,
  Drawer,
  IconButton,
  List, // Keep List for structure if desired, or remove if directly using FormControls
  ListItem, // May remove if not using for filter structure
  ListItemText, // May remove
  Divider,
  useTheme,
  Typography, // Added
  FormControl, // Added
  InputLabel, // Added
  Select, // Added
  MenuItem, // Added
  FormGroup, // Added
  FormControlLabel, // Added
  Checkbox // Added
} from '@mui/material';
import { Close } from '@mui/icons-material';

interface DashboardSidebarProps {
  open: boolean;
  onClose: () => void;
  width?: number;
}

export function DashboardSidebar({ 
  open = false, 
  onClose, 
  width = 320
}: DashboardSidebarProps) {
  const theme = useTheme();

  // Placeholder data for filters - actual values would come from data or be dynamic
  const ratings = ['I', 'II', 'III', 'IV', 'V', 'II-III', 'III-IV'];
  const sizes = ['XS', 'VS', 'S', 'M', 'L'];

  const content = (
    <Box
      sx={{
        height: '100%',
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary, // Changed to use theme color
        display: 'flex',
        flexDirection: 'column',
        p: 2, // Added padding for content
      }}
    >
      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between', // To space title and close button
        alignItems: 'center',
        mb: 2, // Added margin bottom
      }}>
        <Typography variant="h6" component="div">
          Filters
        </Typography>
        <IconButton
          onClick={onClose}
          sx={{ color: theme.palette.text.primary }} // Changed to use theme color
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
          value={[]} // Placeholder - actual value would be state
          onChange={() => { /* Placeholder - actual handler */ }}
          label="Rating"
          renderValue={(selected) => (selected as string[]).join(', ')}
        >
          {ratings.map((rating) => (
            <MenuItem key={rating} value={rating}>
              <Checkbox checked={false /* Placeholder */} />
              <ListItemText primary={rating} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Divider sx={{ mb: 2, borderColor: theme.palette.divider }} />

      {/* Filter by Size */}
      <Typography variant="subtitle1" gutterBottom component="div">
        Size
      </Typography>
      <FormGroup sx={{ mb: 2 }}>
        {sizes.map((size) => (
          <FormControlLabel
            key={size}
            control={<Checkbox checked={false /* Placeholder */} onChange={() => { /* Placeholder */}} name={size} />}
            label={size}
          />
        ))}
      </FormGroup>

      {/* Add more filters as needed, e.g., for Quality, Level, Trend */}

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
          border: 'none'
        }
      }}
    >
      {content}
    </Drawer>
  );
}
