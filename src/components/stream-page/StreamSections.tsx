import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  useTheme,
} from '@mui/material';
import { StreamSection } from '../../types/streamContent';

interface StreamSectionsProps {
  sections: StreamSection[];
}

export function StreamSections({ sections }: StreamSectionsProps) {
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
        Sections
      </Typography>
      <Grid container spacing={2}>
        {sections.map((section, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card
              variant="outlined"
              sx={{
                height: '100%',
                bgcolor:
                  theme.palette.mode === 'dark'
                    ? 'rgba(255,255,255,0.03)'
                    : 'rgba(0,0,0,0.02)',
              }}
            >
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                  {section.name}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                  {section.rating && (
                    <Chip label={section.rating} size="small" color="primary" />
                  )}
                  {section.distance && (
                    <Chip
                      label={section.distance}
                      size="small"
                      variant="outlined"
                    />
                  )}
                  {section.gradient && (
                    <Chip
                      label={section.gradient}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>
                {section.character && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 1 }}
                  >
                    {section.character}
                  </Typography>
                )}
                {section.notes && (
                  <Typography variant="body2" color="text.secondary">
                    {section.notes}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
