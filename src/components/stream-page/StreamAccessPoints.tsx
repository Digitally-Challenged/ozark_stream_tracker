import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
} from '@mui/material';
import { Place } from '@mui/icons-material';
import { AccessPoint } from '../../types/streamContent';

interface StreamAccessPointsProps {
  accessPoints: AccessPoint[];
}

export function StreamAccessPoints({ accessPoints }: StreamAccessPointsProps) {
  const theme = useTheme();

  return (
    <Box sx={{ mb: 4 }}>
      <Typography
        variant="h6"
        sx={{
          mb: 2,
          fontWeight: 600,
          color: theme.palette.text.primary,
          borderBottom: `2px solid ${theme.palette.primary.main}`,
          pb: 1,
          display: 'inline-block',
        }}
      >
        Access Points
      </Typography>
      <List disablePadding>
        {accessPoints.map((point, index) => (
          <ListItem
            key={index}
            sx={{
              bgcolor:
                theme.palette.mode === 'dark'
                  ? 'rgba(255,255,255,0.03)'
                  : 'rgba(0,0,0,0.02)',
              borderRadius: 1,
              mb: 1,
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <Place color="primary" />
            </ListItemIcon>
            <ListItemText
              primary={point.name}
              secondary={
                <>
                  {point.location && <span>{point.location}</span>}
                  {point.location && point.notes && ' — '}
                  {point.notes && <span>{point.notes}</span>}
                </>
              }
              primaryTypographyProps={{ fontWeight: 500 }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
