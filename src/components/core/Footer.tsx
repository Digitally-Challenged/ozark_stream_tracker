import { Box, Container, Typography, Link } from '@mui/material';
import { useTheme } from '@mui/material/styles';

export function Footer() {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: theme.palette.background.paper,
        borderTop: 1,
        borderColor: theme.palette.divider,
      }}
    >
      <Container maxWidth="sm">
        <Typography
          variant="body2"
          color="text.secondary"
          align="center"
        >
          ©{' '}
          <Link
            href="#"
            sx={{
              color: 'inherit',
              textDecoration: 'none',
              transition: 'all 0.2s',
              '&:hover': {
                color: 'primary.main',
                textDecoration: 'underline',
              },
            }}
          >
            Mountain Stream Tracker
          </Link>{' '}
          {new Date().getFullYear()}
        </Typography>
      </Container>
    </Box>
  );
}
