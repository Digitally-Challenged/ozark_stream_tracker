import { useParams, useNavigate } from 'react-router-dom';
import { Box, Container, Button, Typography, useTheme } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { getStreamContent } from '../data/streamContent.generated';
import { StreamHeader } from '../components/stream-page/StreamHeader';
import { StreamDescription } from '../components/stream-page/StreamDescription';
import { StreamSections } from '../components/stream-page/StreamSections';
import { StreamAccessPoints } from '../components/stream-page/StreamAccessPoints';
import { StreamImages } from '../components/stream-page/StreamImages';
import { StreamHazards } from '../components/stream-page/StreamHazards';
import { StreamSources } from '../components/stream-page/StreamSources';
import { streams } from '../data/streamData';

export function StreamPage() {
  const { streamId } = useParams<{ streamId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();

  const content = streamId ? getStreamContent(streamId) : null;

  // Find the corresponding StreamData for live gauge info
  const streamData = streams.find(
    (s) =>
      s.name.toLowerCase().replace(/[^a-z0-9]+/g, '-') === streamId ||
      s.name
        .toLowerCase()
        .includes(content?.name.toLowerCase().split(' ')[0] || '')
  );

  if (!content) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/dashboard')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h5" color="error">
          Stream not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4, flex: 1 }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/dashboard')}
        sx={{
          mb: 3,
          color: theme.palette.text.secondary,
          '&:hover': {
            color: theme.palette.primary.main,
          },
        }}
      >
        Back to Dashboard
      </Button>

      <Box
        sx={{
          bgcolor: theme.palette.background.paper,
          borderRadius: 2,
          overflow: 'hidden',
          boxShadow: theme.shadows[2],
        }}
      >
        <StreamHeader content={content} streamData={streamData} />

        <Box sx={{ p: { xs: 2, md: 4 } }}>
          {content.description && (
            <StreamDescription description={content.description} />
          )}

          {content.sections.length > 0 && (
            <StreamSections sections={content.sections} />
          )}

          {content.accessPoints.length > 0 && (
            <StreamAccessPoints accessPoints={content.accessPoints} />
          )}

          {content.hazards.length > 0 && (
            <StreamHazards hazards={content.hazards} />
          )}

          {content.images.length > 0 && (
            <StreamImages images={content.images} />
          )}

          {content.sources.length > 0 && (
            <StreamSources sources={content.sources} />
          )}
        </Box>
      </Box>
    </Container>
  );
}
