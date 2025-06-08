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
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Save,
  AutoAwesome,
  ArrowBack,
  Edit,
  Visibility,
  ExpandMore,
  TrendingUp,
  FormatSize,
  Palette,
  Settings,
} from '@mui/icons-material';
import { storyApi, generationApi, Story, Chapter, ChapterExpandRequest } from '../services/api';

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

  // Chapter expansion state
  const [expandMenuAnchor, setExpandMenuAnchor] = useState<null | HTMLElement>(null);
  const [expanding, setExpanding] = useState(false);
  const [expandDialogOpen, setExpandDialogOpen] = useState(false);
  const [expansionType, setExpansionType] = useState<'enhance' | 'lengthen' | 'detail' | 'prose'>('enhance');
  const [customPrompt, setCustomPrompt] = useState('');
  const [targetLength, setTargetLength] = useState<number | ''>('');

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

  const handleExpandChapter = async (type: 'enhance' | 'lengthen' | 'detail' | 'prose') => {
    if (!story || !chapter) return;

    setExpanding(true);
    setExpandMenuAnchor(null);

    try {
      const expandRequest: ChapterExpandRequest = {
        expansion_type: type,
        custom_prompt: customPrompt || undefined,
        target_length: targetLength ? Number(targetLength) : undefined,
      };

      const result = await generationApi.expandChapter(story.story_id, chapter.number, expandRequest);

      if (result.success && result.expanded_content) {
        // Update the chapter content with expanded version
        setEditedContent(result.expanded_content);
        setChapter(prev => prev ? { ...prev, content: result.expanded_content!, word_count: result.expanded_word_count || prev.word_count } : null);
        setEditMode(true); // Enter edit mode to review the expansion
      }
    } catch (error) {
      console.error('Failed to expand chapter:', error);
    } finally {
      setExpanding(false);
      setExpandDialogOpen(false);
      setCustomPrompt('');
      setTargetLength('');
    }
  };

  const handleExpandMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setExpandMenuAnchor(event.currentTarget);
  };

  const handleExpandMenuClose = () => {
    setExpandMenuAnchor(null);
  };

  const handleCustomExpand = () => {
    setExpandMenuAnchor(null);
    setExpandDialogOpen(true);
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
                    <>
                      <Button
                        variant="outlined"
                        startIcon={<Edit />}
                        onClick={() => setEditMode(true)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<TrendingUp />}
                        onClick={handleExpandMenuClick}
                        disabled={expanding}
                      >
                        {expanding ? 'Expanding...' : 'Expand Chapter'}
                      </Button>
                    </>
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

      {/* Expansion Menu */}
      <Menu
        anchorEl={expandMenuAnchor}
        open={Boolean(expandMenuAnchor)}
        onClose={handleExpandMenuClose}
      >
        <MenuItem onClick={() => handleExpandChapter('enhance')}>
          <ListItemIcon>
            <AutoAwesome fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Enhance"
            secondary="Improve prose quality and readability"
          />
        </MenuItem>
        <MenuItem onClick={() => handleExpandChapter('lengthen')}>
          <ListItemIcon>
            <FormatSize fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Lengthen"
            secondary="Significantly expand content"
          />
        </MenuItem>
        <MenuItem onClick={() => handleExpandChapter('detail')}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Add Details"
            secondary="Rich sensory descriptions"
          />
        </MenuItem>
        <MenuItem onClick={() => handleExpandChapter('prose')}>
          <ListItemIcon>
            <Palette fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Improve Prose"
            secondary="Sophisticated language and style"
          />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleCustomExpand}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Custom Expansion"
            secondary="Advanced options"
          />
        </MenuItem>
      </Menu>

      {/* Custom Expansion Dialog */}
      <Dialog open={expandDialogOpen} onClose={() => setExpandDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Custom Chapter Expansion</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Expansion Type</InputLabel>
              <Select
                value={expansionType}
                label="Expansion Type"
                onChange={(e) => setExpansionType(e.target.value as any)}
              >
                <MenuItem value="enhance">Enhance - Improve prose quality</MenuItem>
                <MenuItem value="lengthen">Lengthen - Expand content significantly</MenuItem>
                <MenuItem value="detail">Detail - Add rich descriptions</MenuItem>
                <MenuItem value="prose">Prose - Sophisticated language</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Target Word Count (optional)"
              type="number"
              value={targetLength}
              onChange={(e) => setTargetLength(e.target.value ? Number(e.target.value) : '')}
              sx={{ mb: 3 }}
              helperText="Leave empty for automatic length"
            />

            <TextField
              fullWidth
              label="Custom Instructions (optional)"
              multiline
              rows={3}
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="e.g., Focus on building tension and adding dialogue..."
              helperText="Specific instructions for the AI expansion"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExpandDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => handleExpandChapter(expansionType)}
            variant="contained"
            disabled={expanding}
          >
            {expanding ? 'Expanding...' : 'Expand Chapter'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChapterEditor;
