import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  LinearProgress,
} from '@mui/material';
import { Add, Edit, Delete, Visibility } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { storyApi, Story, CreateStoryRequest, generationApi } from '../services/api';

const StoryList: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [complexityInfo, setComplexityInfo] = useState<any>(null);
  const [newStory, setNewStory] = useState<CreateStoryRequest>({
    title: '',
    description: '',
    genre: '',
    target_chapters: 20,
    target_word_count: 80000,
  });
  const navigate = useNavigate();

  const genres = [
    'Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Thriller',
    'Horror', 'Historical Fiction', 'Literary Fiction', 'Adventure', 'Young Adult'
  ];

  useEffect(() => {
    loadStories();
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

  const loadStories = async () => {
    try {
      const data = await storyApi.getStories();
      setStories(data);
    } catch (error) {
      console.error('Failed to load stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStory = async () => {
    try {
      const story = await storyApi.createStory(newStory);
      setStories([...stories, story]);
      setOpenDialog(false);
      setNewStory({
        title: '',
        description: '',
        genre: '',
        target_chapters: 20,
        target_word_count: 80000,
      });
      navigate(`/stories/${story.story_id}`);
    } catch (error) {
      console.error('Failed to create story:', error);
    }
  };

  const handleDeleteStory = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this story?')) {
      try {
        await storyApi.deleteStory(id);
        setStories(stories.filter(story => story.story_id !== id));
      } catch (error) {
        console.error('Failed to delete story:', error);
      }
    }
  };

  const getProgressPercentage = (story: Story) => {
    if (!story.chapters) return 0;
    const generatedChapters = story.chapters.filter(ch => ch.is_generated).length;
    return story.target_chapters > 0 ? (generatedChapters / story.target_chapters) * 100 : 0;
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
          <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
            Loading stories...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          My Stories
        </Typography>
        
        {stories.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 8 }}>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              No stories yet
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Create your first AI-powered novel to get started!
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<Add />}
              onClick={() => setOpenDialog(true)}
            >
              Create Your First Story
            </Button>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {stories.map((story) => (
              <Grid size={{ xs: 12, md: 6, lg: 4 }} key={story.story_id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {story.title}
                    </Typography>
                    
                    {story.genre && (
                      <Chip 
                        label={story.genre} 
                        size="small" 
                        color="primary" 
                        sx={{ mb: 1 }} 
                      />
                    )}
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {story.description || 'No description'}
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" display="block">
                        Progress: {Math.round(getProgressPercentage(story))}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={getProgressPercentage(story)} 
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                    
                    <Typography variant="caption" color="text.secondary">
                      {story.total_word_count || 0} / {story.target_word_count} words
                    </Typography>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<Visibility />}
                      onClick={() => navigate(`/stories/${story.story_id}`)}
                    >
                      View
                    </Button>
                    <Button
                      size="small"
                      startIcon={<Delete />}
                      color="error"
                      onClick={() => handleDeleteStory(story.story_id)}
                    >
                      Delete
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setOpenDialog(true)}
      >
        <Add />
      </Fab>

      {/* Create Story Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Story</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            variant="outlined"
            value={newStory.title}
            onChange={(e) => setNewStory({ ...newStory, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newStory.description}
            onChange={(e) => setNewStory({ ...newStory, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <TextField
            select
            margin="dense"
            label="Genre"
            fullWidth
            variant="outlined"
            value={newStory.genre}
            onChange={(e) => setNewStory({ ...newStory, genre: e.target.value })}
            sx={{ mb: 2 }}
          >
            {genres.map((genre) => (
              <MenuItem key={genre} value={genre}>
                {genre}
              </MenuItem>
            ))}
          </TextField>

          {complexityInfo && (
            <TextField
              select
              margin="dense"
              label="Writing Complexity"
              fullWidth
              variant="outlined"
              value={complexityInfo.current_complexity}
              onChange={async (e) => {
                try {
                  await generationApi.setComplexity(e.target.value);
                  setComplexityInfo({ ...complexityInfo, current_complexity: e.target.value });
                } catch (error) {
                  console.error('Failed to set complexity:', error);
                }
              }}
              sx={{ mb: 2 }}
              helperText={complexityInfo.descriptions[complexityInfo.current_complexity]}
            >
              {complexityInfo.available_levels.map((level: string) => (
                <MenuItem key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          )}
          
          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField
                margin="dense"
                label="Target Chapters"
                type="number"
                fullWidth
                variant="outlined"
                value={newStory.target_chapters}
                onChange={(e) => setNewStory({ ...newStory, target_chapters: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                margin="dense"
                label="Target Word Count"
                type="number"
                fullWidth
                variant="outlined"
                value={newStory.target_word_count}
                onChange={(e) => setNewStory({ ...newStory, target_word_count: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateStory} 
            variant="contained"
            disabled={!newStory.title.trim()}
          >
            Create Story
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StoryList;
