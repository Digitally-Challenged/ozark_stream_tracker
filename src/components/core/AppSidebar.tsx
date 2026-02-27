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
import { Close, Favorite } from '@mui/icons-material';

interface AppSidebarProps {
  open: boolean;
  onClose: () => void;
}

export function AppSidebar({ open, onClose }: AppSidebarProps) {
  const menuItems = [
    { text: 'Learn More', href: '#', disabled: true },
    {
      text: 'Contact',
      href: 'mailto:contact@ozarkstreamtracker.com',
      disabled: false,
    },
    { text: 'Trail Finder', href: '#', disabled: true },
  ];

  const donationItems = [
    { text: 'Buy us a coffee!', href: '#', disabled: true },
    { text: 'Venmo', href: '#', disabled: true },
    { text: 'PayPal', href: '#', disabled: true },
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
          backgroundColor: 'background.default',
          color: 'text.primary',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <IconButton onClick={onClose} sx={{ color: 'text.primary' }}>
          <Close />
        </IconButton>
      </Box>

      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component="a"
              href={item.disabled ? undefined : item.href}
              disabled={item.disabled}
              onClick={item.disabled ? undefined : onClose}
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
          <Favorite sx={{ color: 'text.primary', fontSize: 20 }} />
          <Typography
            variant="h6"
            sx={{ color: 'text.primary', fontSize: '1.1rem' }}
          >
            Love the app?
          </Typography>
        </Box>
        <Divider sx={{ bgcolor: 'divider' }} />
      </Box>

      <List>
        {donationItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component="a"
              href={item.disabled ? undefined : item.href}
              target={item.disabled ? undefined : '_blank'}
              rel={item.disabled ? undefined : 'noopener noreferrer'}
              disabled={item.disabled}
              onClick={item.disabled ? undefined : onClose}
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
