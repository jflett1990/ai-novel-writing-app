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
  Snackbar,
  Fab,
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
  Speed,
  HighQuality,
  Analytics,
  Refresh,
} from '@mui/icons-material';
import { 
  storyApi, 
  generationApi, 
  Story, 
  Chapter, 
  ChapterExpandRequest,
  GenerationMode,
  EnhancedGenerationRequest,
  FeatureAvailabilityResponse,
  QualityAnalysisResponse,
  MultiPassGenerationResponse,
} from '../services/api';

// Import our new components
import EnhancedGenerationControls from '../components/EnhancedGenerationControls';
import QualityIndicator from '../components/QualityIndicator';
import ChapterAnalysis from '../components/ChapterAnalysis';

const ChapterEditor: React.FC = () => {
  const { id, chapterNumber } = useParams<{ id: string; chapterNumber: string }>();
  const navigate = useNavigate();
  
  // Basic state
  const [story, setStory] = useState<Story | null>(null);
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  // Enhanced generation state
  const [generationMode, setGenerationMode] = useState<GenerationMode>('standard');
  const [targetWordCount, setTargetWordCount] = useState(2500);
  const [qualityCheck, setQualityCheck] = useState(true);
  const [featuresAvailable, setFeaturesAvailable] = useState<FeatureAvailabilityResponse>({
    enhanced_generation: false,
    multi_pass_generation: false,
    quality_analysis: false,
    custom_prompting: false,
  });

  // Multi-pass generation state
  const [multiPassGenerating, setMultiPassGenerating] = useState(false);
  const [lastGenerationResult, setLastGenerationResult] = useState<MultiPassGenerationResponse | null>(null);

  // Chapter expansion state (keeping existing functionality)
  const [expandMenuAnchor, setExpandMenuAnchor] = useState<null | HTMLElement>(null);
  const [expanding, setExpanding] = useState(false);
  const [expandDialogOpen, setExpandDialogOpen] = useState(false);
  const [expansionType, setExpansionType] = useState<'enhance' | 'lengthen' | 'detail' | 'prose'>('enhance');
  const [customPrompt, setCustomPrompt] = useState('');
  const [targetLength, setTargetLength] = useState<number | ''>('');

  // UI state
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Load data on component mount
  useEffect(() => {
    if (id && chapterNumber) {
      loadChapterData(parseInt(id), parseInt(chapterNumber));
      checkFeatureAvailability();
    }
  }, [id, chapterNumber]);

  const checkFeatureAvailability = async () => {
    try {
      const features = await generationApi.getFeatures();
      setFeaturesAvailable(features);
      
      // Default to enhanced mode if available
      if (features.enhanced_generation) {
        setGenerationMode('enhanced');
      }
    } catch (error) {
      console.warn('Could not check feature availability:', error);
      // Gracefully degrade to standard mode
      setGenerationMode('standard');
    }
  };

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
      setSnackbarMessage('Failed to load chapter data');
      setSnackbarOpen(true);
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
      setSnackbarMessage('Chapter saved successfully');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Failed to save chapter:', error);
      setSnackbarMessage('Failed to save chapter');
      setSnackbarOpen(true);
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async () => {
    if (!story || !chapter) return;

    setGenerating(true);
    try {
      if (generationMode === 'enhanced' && featuresAvailable.enhanced_generation) {
        // Use enhanced generation
        const request: EnhancedGenerationRequest = {
          target_word_count: targetWordCount,
          quality_check: qualityCheck,
        };

        const result = await generationApi.generateChapterEnhanced(
          story.story_id, 
          chapter.number, 
          request
        );

        if (result.success && result.chapter_content) {
          setEditedContent(result.chapter_content);
          setChapter(prev => prev ? { 
            ...prev, 
            content: result.chapter_content!,
            word_count: result.word_count || prev.word_count,
            quality_score: result.quality_score,
          } : null);
          setEditMode(true);
          setSnackbarMessage(`Chapter generated successfully! Quality: ${result.quality_score ? (result.quality_score * 100).toFixed(0) + '%' : 'N/A'}`);
          setSnackbarOpen(true);
        } else {
          throw new Error(result.error || 'Enhanced generation failed');
        }
      } else {
        // Use standard generation
        const result = await generationApi.generateChapter(story.story_id, chapter.number);
        if (result.success) {
          // Reload chapter data
          await loadChapterData(story.story_id, chapter.number);
          setSnackbarMessage('Chapter generated successfully');
          setSnackbarOpen(true);
        }
      }
    } catch (error) {
      console.error('Failed to generate chapter:', error);
      setSnackbarMessage('Failed to generate chapter');
      setSnackbarOpen(true);
    } finally {
      setGenerating(false);
    }
  };

  const handleMultiPassGenerate = async () => {
    if (!story || !chapter || !featuresAvailable.multi_pass_generation) return;

    setMultiPassGenerating(true);
    try {
      const request: EnhancedGenerationRequest = {
        target_word_count: targetWordCount,
        quality_check: true, // Always enable for multi-pass
      };

      const result = await generationApi.generateChapterMultiPass(
        story.story_id, 
        chapter.number, 
        request
      );

      if (result.success && result.chapter_content) {
        setEditedContent(result.chapter_content);
        setChapter(prev => prev ? { 
          ...prev, 
          content: result.chapter_content!,
          word_count: result.word_count || prev.word_count,
          quality_score: result.quality_score,
        } : null);
        setLastGenerationResult(result);
        setEditMode(true);
        setSnackbarMessage(
          `High-quality chapter generated in ${result.passes_completed} passes! ` +
          `Quality: ${result.quality_score ? (result.quality_score * 100).toFixed(0) + '%' : 'N/A'}`
        );
        setSnackbarOpen(true);
      } else {
        throw new Error(result.error || 'Multi-pass generation failed');
      }
    } catch (error) {
      console.error('Failed to generate chapter with multi-pass:', error);
      setSnackbarMessage('Failed to generate high-quality chapter');
      setSnackbarOpen(true);
    } finally {
      setMultiPassGenerating(false);
    }
  };

  const handleAnalyzeQuality = async (): Promise<QualityAnalysisResponse> => {
    if (!story || !chapter) {
      throw new Error('Story or chapter not available');
    }

    return await generationApi.analyzeChapterQuality(story.story_id, chapter.number);
  };

  // Keep existing expand functionality
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
        setEditedContent(result.expanded_content);
        setChapter(prev => prev ? { 
          ...prev, 
          content: result.expanded_content!, 
          word_count: result.expanded_word_count || prev.word_count 
        } : null);
        setEditMode(true);
        setSnackbarMessage('Chapter expanded successfully');
        setSnackbarOpen(true);
      }
    } catch (error) {
      console.error('Failed to expand chapter:', error);
      setSnackbarMessage('Failed to expand chapter');
      setSnackbarOpen(true);
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
            {chapter.quality_score && (
              <Chip 
                label={`Quality: ${(chapter.quality_score * 100).toFixed(0)}%`} 
                color="info" 
                size="small" 
              />
            )}
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {chapter.summary}
          </Typography>
        </Box>

        {/* Enhanced Generation Controls */}
        {!chapter.content && (
          <EnhancedGenerationControls
            generationMode={generationMode}
            onGenerationModeChange={setGenerationMode}
            targetWordCount={targetWordCount}
            onTargetWordCountChange={setTargetWordCount}
            qualityCheck={qualityCheck}
            onQualityCheckChange={setQualityCheck}
            enhancedAvailable={featuresAvailable.enhanced_generation}
            loading={generating || multiPassGenerating}
            qualityScore={chapter.quality_score}
          />
        )}

        <Grid container spacing={3}>
          {/* Main Editor */}
          <Grid size={{ xs: 12, md: 9 }}>
            <Paper sx={{ p: 3 }}>
              {/* Toolbar */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="h6">
                    Content ({wordCount.toLocaleString()} words)
                  </Typography>
                  
                  {chapter.quality_score && (
                    <QualityIndicator
                      qualityScore={chapter.quality_score}
                      wordCount={wordCount}
                      targetWordCount={targetWordCount}
                      passesCompleted={lastGenerationResult?.passes_completed}
                      generationTime={lastGenerationResult?.generation_time}
                      modelUsed={lastGenerationResult?.model_used}
                      compact
                    />
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!chapter.content && (
                    <>
                      <Button
                        variant="contained"
                        startIcon={generating ? <CircularProgress size={16} /> : <AutoAwesome />}
                        onClick={handleGenerate}
                        disabled={generating || multiPassGenerating}
                      >
                        {generating ? 'Generating...' : `Generate ${generationMode === 'enhanced' ? '(Enhanced)' : ''}`}
                      </Button>
                      
                      {featuresAvailable.multi_pass_generation && (
                        <Button
                          variant="contained"
                          color="secondary"
                          startIcon={multiPassGenerating ? <CircularProgress size={16} /> : <HighQuality />}
                          onClick={handleMultiPassGenerate}
                          disabled={generating || multiPassGenerating}
                        >
                          {multiPassGenerating ? 'Generating...' : 'High Quality'}
                        </Button>
                      )}
                    </>
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
              {!chapter.content && !generating && !multiPassGenerating ? (
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
                    disabled={generating || multiPassGenerating}
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
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Chapter Info */}
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

              {/* Quality Metrics */}
              {chapter.quality_score && (
                <QualityIndicator
                  qualityScore={chapter.quality_score}
                  wordCount={wordCount}
                  targetWordCount={targetWordCount}
                  passesCompleted={lastGenerationResult?.passes_completed}
                  generationTime={lastGenerationResult?.generation_time}
                  modelUsed={lastGenerationResult?.model_used}
                />
              )}

              {/* Chapter Analysis */}
              {chapter.content && featuresAvailable.quality_analysis && (
                <ChapterAnalysis
                  storyId={story.story_id}
                  chapterNumber={chapter.number}
                  onAnalyze={handleAnalyzeQuality}
                  loading={generating || multiPassGenerating}
                />
              )}
            </Box>
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

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default ChapterEditor;