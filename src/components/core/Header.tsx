import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, useTheme as useMuiTheme } from '@mui/material';
import { Moon, Sun, Droplets } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export function Header() {
  const { mode, toggleColorMode } = useTheme();
  const theme = useMuiTheme();

  return (
    <AppBar position="static" elevation={0}>
      <Toolbar>
        <Droplets className="mr-2" />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Mountain Stream Tracker
        </Typography>
        <IconButton onClick={toggleColorMode} color="inherit">
          {mode === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}