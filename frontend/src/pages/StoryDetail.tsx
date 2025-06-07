import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore,
  AutoAwesome,
  Edit,
  People,
  Public,
  MenuBook,
  PlayArrow,
} from '@mui/icons-material';
import { storyApi, generationApi, Story, Character } from '../services/api';

const StoryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [story, setStory] = useState<Story | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadStoryData(parseInt(id));
    }
  }, [id]);

  const loadStoryData = async (storyId: number) => {
    try {
      const [storyData, charactersData] = await Promise.all([
        storyApi.getStory(storyId),
        storyApi.getCharacters(storyId),
      ]);
      setStory(storyData);
      setCharacters(charactersData);
    } catch (error) {
      console.error('Failed to load story data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateOutline = async () => {
    if (!story) return;
    
    setGenerating('outline');
    try {
      await generationApi.generateOutline(story.story_id, {
        target_chapters: story.target_chapters,
      });
      // Reload story data to get the new outline
      await loadStoryData(story.story_id);
    } catch (error) {
      console.error('Failed to generate outline:', error);
    } finally {
      setGenerating(null);
    }
  };

  const handleGenerateCharacters = async () => {
    if (!story) return;
    
    setGenerating('characters');
    try {
      await generationApi.generateCharacters(story.story_id, {
        character_count: 4,
      });
      // Reload characters
      const charactersData = await storyApi.getCharacters(story.story_id);
      setCharacters(charactersData);
    } catch (error) {
      console.error('Failed to generate characters:', error);
    } finally {
      setGenerating(null);
    }
  };

  const handleGenerateChapter = async (chapterNumber: number) => {
    if (!story) return;
    
    setGenerating(`chapter-${chapterNumber}`);
    try {
      await generationApi.generateChapter(story.story_id, chapterNumber);
      // Reload story data to get the updated chapter
      await loadStoryData(story.story_id);
    } catch (error) {
      console.error('Failed to generate chapter:', error);
    } finally {
      setGenerating(null);
    }
  };

  const getProgressPercentage = () => {
    if (!story?.chapters) return 0;
    const generatedChapters = story.chapters.filter(ch => ch.is_generated).length;
    return story.target_chapters > 0 ? (generatedChapters / story.target_chapters) * 100 : 0;
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!story) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 4 }}>
          Story not found
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Story Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            {story.title}
          </Typography>
          
          {story.genre && (
            <Chip label={story.genre} color="primary" sx={{ mb: 2 }} />
          )}
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {story.description}
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{story.total_word_count || 0}</Typography>
                  <Typography variant="caption">Words Written</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{story.chapters?.filter(ch => ch.is_generated).length || 0}</Typography>
                  <Typography variant="caption">Chapters Generated</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{story.character_count || 0}</Typography>
                  <Typography variant="caption">Characters</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{Math.round(getProgressPercentage())}%</Typography>
                  <Typography variant="caption">Complete</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <LinearProgress 
            variant="determinate" 
            value={getProgressPercentage()} 
            sx={{ mb: 3, height: 8, borderRadius: 4 }}
          />
        </Box>

        <Grid container spacing={3}>
          {/* Main Content */}
          <Grid size={{ xs: 12, md: 8 }}>
            {/* Outline Section */}
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <MenuBook sx={{ mr: 1 }} />
                <Typography variant="h6">Story Outline</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {!story.chapters || story.chapters.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      No outline generated yet
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AutoAwesome />}
                      onClick={handleGenerateOutline}
                      disabled={generating === 'outline'}
                    >
                      {generating === 'outline' ? 'Generating...' : 'Generate Outline'}
                    </Button>
                  </Box>
                ) : (
                  <List>
                    {story.chapters.map((chapter) => (
                      <React.Fragment key={chapter.chapter_id}>
                        <ListItemButton
                          onClick={() => navigate(`/stories/${story.story_id}/chapters/${chapter.number}`)}
                        >
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">
                                  Chapter {chapter.number}: {chapter.title}
                                </Typography>
                                {chapter.is_generated && (
                                  <Chip label="Generated" size="small" color="success" />
                                )}
                              </Box>
                            }
                            secondary={chapter.summary}
                          />
                          {!chapter.is_generated && (
                            <Button
                              size="small"
                              startIcon={<PlayArrow />}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleGenerateChapter(chapter.number);
                              }}
                              disabled={generating === `chapter-${chapter.number}`}
                            >
                              {generating === `chapter-${chapter.number}` ? 'Generating...' : 'Generate'}
                            </Button>
                          )}
                        </ListItemButton>
                        <Divider />
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Sidebar */}
          <Grid size={{ xs: 12, md: 4 }}>
            {/* Characters Section */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <People sx={{ mr: 1 }} />
                <Typography variant="h6">Characters ({characters.length})</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {characters.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      No characters yet
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<AutoAwesome />}
                      onClick={handleGenerateCharacters}
                      disabled={generating === 'characters'}
                    >
                      {generating === 'characters' ? 'Generating...' : 'Generate Characters'}
                    </Button>
                  </Box>
                ) : (
                  <List dense>
                    {characters.map((character) => (
                      <ListItem key={character.character_id}>
                        <ListItemText
                          primary={character.name}
                          secondary={character.role}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </AccordionDetails>
            </Accordion>

            {/* World Building Section */}
            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Public sx={{ mr: 1 }} />
                <Typography variant="h6">World Building</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  World building features coming soon...
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default StoryDetail;
