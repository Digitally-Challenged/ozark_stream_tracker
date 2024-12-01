import { 
  Box, 
  Drawer, 
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider
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
  const menuItems = [
    { label: 'Learn More', href: '/learn' },
    { label: 'Contact', href: '/contact' },
    { label: 'Trail Finder', href: '/trails' },
    { label: '❤️ the app?', href: '/feedback' },
    { label: 'Buy us a coffee!', href: '/support' },
    { label: 'Venmo', href: '/venmo' },
    { label: 'PayPal', href: '/paypal' }
  ];

  const content = (
    <Box
      sx={{
        height: '100%',
        backgroundColor: 'rgb(17, 24, 39)',
        color: 'white',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'flex-end',
        p: 2
      }}>
        <IconButton 
          onClick={onClose} 
          sx={{ color: 'white' }}
        >
          <Close />
        </IconButton>
      </Box>

      <List sx={{ flex: 1, pt: 0 }}>
        {menuItems.map((item, index) => (
          <Box key={item.label}>
            <ListItem disablePadding>
              <ListItemButton
                sx={{
                  py: 2,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    sx: {
                      color: 'white',
                      fontSize: '1rem',
                      fontWeight: 400
                    }
                  }}
                />
              </ListItemButton>
            </ListItem>
            {index < menuItems.length - 1 && (
              <Divider 
                sx={{ 
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  mx: 2
                }} 
              />
            )}
          </Box>
        ))}
      </List>
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
          backgroundColor: 'rgb(17, 24, 39)',
          border: 'none'
        }
      }}
    >
      {content}
    </Drawer>
  );
}
