import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Save,
  AutoAwesome,
  ArrowBack,
  Edit,
  Visibility,
} from '@mui/icons-material';
import { storyApi, generationApi, Story, Chapter } from '../services/api';

const ChapterEditor: React.FC = () => {
  const { id, chapterNumber } = useParams<{ id: string; chapterNumber: string }>();
  const navigate = useNavigate();
  const [story, setStory] = useState<Story | null>(null);
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  useEffect(() => {
    if (id && chapterNumber) {
      loadChapterData(parseInt(id), parseInt(chapterNumber));
    }
  }, [id, chapterNumber]);

  const loadChapterData = async (storyId: number, chapterNum: number) => {
    try {
      const [storyData, chapterData] = await Promise.all([
        storyApi.getStory(storyId),
        storyApi.getChapter(storyId, chapterNum),
      ]);
      setStory(storyData);
      setChapter(chapterData);
      setEditedContent(chapterData.content || '');
    } catch (error) {
      console.error('Failed to load chapter data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!story || !chapter) return;
    
    setSaving(true);
    try {
      const updatedChapter = await storyApi.updateChapter(
        story.story_id,
        chapter.number,
        { content: editedContent }
      );
      setChapter(updatedChapter);
      setEditMode(false);
    } catch (error) {
      console.error('Failed to save chapter:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async () => {
    if (!story || !chapter) return;
    
    setGenerating(true);
    try {
      const result = await generationApi.generateChapter(story.story_id, chapter.number);
      if (result.success) {
        // Reload chapter data
        await loadChapterData(story.story_id, chapter.number);
      }
    } catch (error) {
      console.error('Failed to generate chapter:', error);
    } finally {
      setGenerating(false);
    }
  };

  const wordCount = editedContent ? editedContent.split(/\s+/).filter(word => word.length > 0).length : 0;

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!story || !chapter) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 4 }}>
          Chapter not found
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate(`/stories/${story.story_id}`)}
            sx={{ mb: 2 }}
          >
            Back to Story
          </Button>
          
          <Typography variant="h4" component="h1" gutterBottom>
            Chapter {chapter.number}: {chapter.title}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            {chapter.is_generated && (
              <Chip label="AI Generated" color="success" size="small" />
            )}
            {chapter.is_approved && (
              <Chip label="Approved" color="primary" size="small" />
            )}
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {chapter.summary}
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Main Editor */}
          <Grid size={{ xs: 12, md: 9 }}>
            <Paper sx={{ p: 3 }}>
              {/* Toolbar */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Content ({wordCount} words)
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!chapter.content && (
                    <Button
                      variant="contained"
                      startIcon={<AutoAwesome />}
                      onClick={handleGenerate}
                      disabled={generating}
                    >
                      {generating ? 'Generating...' : 'Generate with AI'}
                    </Button>
                  )}
                  
                  {chapter.content && !editMode && (
                    <Button
                      variant="outlined"
                      startIcon={<Edit />}
                      onClick={() => setEditMode(true)}
                    >
                      Edit
                    </Button>
                  )}
                  
                  {editMode && (
                    <>
                      <Button
                        variant="outlined"
                        onClick={() => {
                          setEditMode(false);
                          setEditedContent(chapter.content || '');
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<Save />}
                        onClick={handleSave}
                        disabled={saving}
                      >
                        {saving ? 'Saving...' : 'Save'}
                      </Button>
                    </>
                  )}
                </Box>
              </Box>
              
              <Divider sx={{ mb: 3 }} />
              
              {/* Content Area */}
              {!chapter.content && !generating ? (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No content yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Generate AI content or start writing manually
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AutoAwesome />}
                    onClick={handleGenerate}
                    disabled={generating}
                  >
                    Generate with AI
                  </Button>
                </Box>
              ) : editMode ? (
                <TextField
                  fullWidth
                  multiline
                  rows={20}
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  placeholder="Start writing your chapter..."
                  variant="outlined"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontFamily: '"Georgia", serif',
                      fontSize: '16px',
                      lineHeight: 1.6,
                    },
                  }}
                />
              ) : (
                <Box
                  sx={{
                    fontFamily: '"Georgia", serif',
                    fontSize: '16px',
                    lineHeight: 1.8,
                    whiteSpace: 'pre-wrap',
                    minHeight: '400px',
                  }}
                >
                  {chapter.content}
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Sidebar */}
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Chapter Info
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Word Count
                  </Typography>
                  <Typography variant="body1">
                    {chapter.word_count || wordCount}
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Status
                  </Typography>
                  <Typography variant="body1">
                    {chapter.is_generated ? 'Generated' : 'Draft'}
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Last Updated
                  </Typography>
                  <Typography variant="body1">
                    {chapter.updated_at ? new Date(chapter.updated_at).toLocaleDateString() : 'Never'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ChapterEditor;
