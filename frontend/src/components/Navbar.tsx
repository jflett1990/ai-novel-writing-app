import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Chip, Menu, MenuItem } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { AutoStories, Add, Settings } from '@mui/icons-material';
import { generationApi } from '../services/api';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const [complexityInfo, setComplexityInfo] = useState<any>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadComplexityInfo();
  }, []);

  const loadComplexityInfo = async () => {
    try {
      const data = await generationApi.getComplexity();
      setComplexityInfo(data);
    } catch (error) {
      console.error('Failed to load complexity info:', error);
    }
  };

  const handleComplexityChange = async (level: string) => {
    try {
      await generationApi.setComplexity(level);
      setComplexityInfo({ ...complexityInfo, current_complexity: level });
      setAnchorEl(null);
    } catch (error) {
      console.error('Failed to set complexity:', error);
    }
  };

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
