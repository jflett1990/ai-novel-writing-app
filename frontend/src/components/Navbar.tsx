import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { AutoStories, Add } from '@mui/icons-material';

const Navbar: React.FC = () => {
  const navigate = useNavigate();

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <AutoStories sx={{ mr: 2 }} />
        <Typography
          variant="h6"
          component={Link}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            fontFamily: '"Playfair Display", serif',
            fontWeight: 'bold',
          }}
        >
          AI Novel Writer
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={Link}
            to="/"
            sx={{ textTransform: 'none' }}
          >
            My Stories
          </Button>
          
          <Button
            color="inherit"
            startIcon={<Add />}
            onClick={() => navigate('/')}
            sx={{ textTransform: 'none' }}
          >
            New Story
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
