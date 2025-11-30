import { Box, Typography, useTheme } from '@mui/material';

interface StreamDescriptionProps {
  description: string;
}

export function StreamDescription({ description }: StreamDescriptionProps) {
  const theme = useTheme();

  // Split into paragraphs
  const paragraphs = description.split('\n\n').filter((p) => p.trim());

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
        Description
      </Typography>
      {paragraphs.map((para, index) => (
        <Typography
          key={index}
          variant="body1"
          sx={{
            mb: 2,
            color: theme.palette.text.secondary,
            lineHeight: 1.8,
          }}
        >
          {para}
        </Typography>
      ))}
    </Box>
  );
}
