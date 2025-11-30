import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Link,
  useTheme,
} from '@mui/material';
import { OpenInNew } from '@mui/icons-material';
import { StreamSource } from '../../types/streamContent';

interface StreamSourcesProps {
  sources: StreamSource[];
}

export function StreamSources({ sources }: StreamSourcesProps) {
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
        Sources & References
      </Typography>
      <List disablePadding>
        {sources.map((source, index) => (
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
              <OpenInNew color="primary" fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary={
                <Link
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  underline="hover"
                  color="primary"
                >
                  {source.title}
                </Link>
              }
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
