import {
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Typography,
} from '@mui/material';
import {
  Close,
  Favorite,
  Coffee,
  AttachMoney,
  Payment,
  Info,
  Email,
  Map,
} from '@mui/icons-material';

interface AppSidebarProps {
  open: boolean;
  onClose: () => void;
}

export function AppSidebar({ open, onClose }: AppSidebarProps) {
  const menuItems = [
    { text: 'Learn More', icon: <Info />, href: '#' },
    {
      text: 'Contact',
      icon: <Email />,
      href: 'mailto:contact@ozarkstreamtracker.com',
    }, // Placeholder
    { text: 'Trail Finder', icon: <Map />, href: '#' },
  ];

  const donationItems = [
    { text: 'Buy us a coffee!', icon: <Coffee />, href: '#' },
    { text: 'Venmo', icon: <AttachMoney />, href: '#' },
    { text: 'PayPal', icon: <Payment />, href: '#' },
  ];

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      variant="temporary"
      PaperProps={{
        sx: {
          width: 280,
          backgroundColor: '#1a1a1a', // Match dark theme or screenshot
          color: 'white',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <IconButton onClick={onClose} sx={{ color: 'white' }}>
          <Close />
        </IconButton>
      </Box>

      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component="a"
              href={item.href}
              onClick={onClose}
              sx={{ py: 1.5 }}
            >
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{ fontSize: '1.1rem' }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Box sx={{ px: 2, py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Favorite sx={{ color: 'white', fontSize: 20 }} />
          <Typography variant="h6" sx={{ color: 'white', fontSize: '1.1rem' }}>
            the app?
          </Typography>
        </Box>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
      </Box>

      <List>
        {donationItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component="a"
              href={item.href}
              target="_blank"
              rel="noopener noreferrer"
              onClick={onClose}
              sx={{ py: 1.5 }}
            >
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{ fontSize: '1.1rem' }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}
