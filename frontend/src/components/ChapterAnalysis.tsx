import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Collapse,
  Alert,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  Analytics,
  ExpandMore,
  ExpandLess,
  CheckCircle,
  Warning,
  Lightbulb,
  Assessment,
  FormatQuote,
  Article,
} from '@mui/icons-material';
import { QualityAnalysisResponse } from '../services/api';

interface ChapterAnalysisProps {
  storyId: number;
  chapterNumber: number;
  onAnalyze: () => Promise<QualityAnalysisResponse>;
  loading?: boolean;
}

const ChapterAnalysis: React.FC<ChapterAnalysisProps> = ({
  storyId,
  chapterNumber,
  onAnalyze,
  loading = false,
}) => {
  const [analysis, setAnalysis] = useState<QualityAnalysisResponse | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await onAnalyze();
      setAnalysis(result);
      setExpanded(true);
    } catch (error) {
      console.error('Failed to analyze chapter:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#22c55e';
    if (score >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Needs Improvement';
  };

  const getSeverityIcon = (type: 'issue' | 'suggestion') => {
    return type === 'issue' ? (
      <Warning sx={{ color: '#f59e0b' }} />
    ) : (
      <Lightbulb sx={{ color: '#3b82f6' }} />
    );
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Analytics />
              Chapter Quality Analysis
            </Box>
          </Typography>
          
          <Button
            variant="outlined"
            startIcon={analyzing ? <CircularProgress size={16} /> : <Assessment />}
            onClick={handleAnalyze}
            disabled={analyzing || loading}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Quality'}
          </Button>
        </Box>

        {analysis && (
          <Collapse in={expanded}>
            <Box sx={{ mt: 3 }}>
              {/* Overall Quality Score */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Overall Quality Score
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.quality_score * 100}
                    sx={{
                      flexGrow: 1,
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: '#f1f5f9',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getScoreColor(analysis.quality_score),
                        borderRadius: 5,
                      },
                    }}
                  />
                  <Typography variant="h6" fontWeight={700}>
                    {(analysis.quality_score * 100).toFixed(0)}%
                  </Typography>
                </Box>
                
                <Chip
                  label={getScoreLabel(analysis.quality_score)}
                  sx={{
                    backgroundColor: getScoreColor(analysis.quality_score),
                    color: 'white',
                    fontWeight: 500,
                  }}
                />
              </Box>

              {/* Detailed Metrics */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Content Metrics
                </Typography>
                
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2 }}>
                  <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                    <Article sx={{ color: '#64748b', mb: 1 }} />
                    <Typography variant="h6" fontWeight={600}>
                      {analysis.word_count.toLocaleString()}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Words
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                    <FormatQuote sx={{ color: '#64748b', mb: 1 }} />
                    <Typography variant="h6" fontWeight={600}>
                      {analysis.dialogue_count}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Dialogue Sections
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#f8fafc', borderRadius: 1 }}>
                    <Assessment sx={{ color: '#64748b', mb: 1 }} />
                    <Typography variant="h6" fontWeight={600}>
                      {analysis.paragraph_count}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Paragraphs
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {/* Additional Scores */}
              {(analysis.style_consistency !== undefined || analysis.readability_score !== undefined) && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Quality Breakdown
                  </Typography>
                  
                  {analysis.style_consistency !== undefined && (
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Style Consistency</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {(analysis.style_consistency * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={analysis.style_consistency * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#f1f5f9',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getScoreColor(analysis.style_consistency),
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>
                  )}
                  
                  {analysis.readability_score !== undefined && (
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Readability</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {(analysis.readability_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={analysis.readability_score * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#f1f5f9',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getScoreColor(analysis.readability_score),
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>
                  )}
                </Box>
              )}

              {/* Issues */}
              {analysis.issues.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ color: '#f59e0b' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Warning />
                      Issues Found ({analysis.issues.length})
                    </Box>
                  </Typography>
                  
                  <List dense>
                    {analysis.issues.map((issue: string, index: number) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {getSeverityIcon('issue')}
                        </ListItemIcon>
                        <ListItemText
                          primary={issue}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Suggestions */}
              {analysis.suggestions.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ color: '#3b82f6' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Lightbulb />
                      Suggestions ({analysis.suggestions.length})
                    </Box>
                  </Typography>
                  
                  <List dense>
                    {analysis.suggestions.map((suggestion: string, index: number) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {getSeverityIcon('suggestion')}
                        </ListItemIcon>
                        <ListItemText
                          primary={suggestion}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* No Issues/Suggestions */}
              {analysis.issues.length === 0 && analysis.suggestions.length === 0 && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircle fontSize="small" />
                    <Typography variant="body2" fontWeight={500}>
                      No issues found! This chapter meets quality standards.
                    </Typography>
                  </Box>
                </Alert>
              )}
            </Box>
          </Collapse>
        )}

        {/* Toggle Button */}
        {analysis && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Button
              size="small"
              onClick={() => setExpanded(!expanded)}
              endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
            >
              {expanded ? 'Hide Details' : 'Show Details'}
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ChapterAnalysis;