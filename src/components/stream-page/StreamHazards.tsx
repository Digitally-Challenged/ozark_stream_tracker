import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
} from '@mui/material';
import { Warning } from '@mui/icons-material';

interface StreamHazardsProps {
  hazards: string[];
}

export function StreamHazards({ hazards }: StreamHazardsProps) {
  const theme = useTheme();

  return (
    <Box sx={{ mb: 4 }}>
      <Typography
        variant="h6"
        sx={{
          mb: 2,
          fontWeight: 600,
          color: theme.palette.text.primary,
          borderBottom: `2px solid ${theme.palette.warning.main}`,
          pb: 1,
          display: 'inline-block',
        }}
      >
        Hazards
      </Typography>
      <List disablePadding>
        {hazards.map((hazard, index) => (
          <ListItem
            key={index}
            sx={{
              bgcolor:
                theme.palette.mode === 'dark'
                  ? 'rgba(255,152,0,0.1)'
                  : 'rgba(255,152,0,0.05)',
              borderRadius: 1,
              mb: 1,
              borderLeft: `3px solid ${theme.palette.warning.main}`,
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <Warning color="warning" />
            </ListItemIcon>
            <ListItemText primary={hazard} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
