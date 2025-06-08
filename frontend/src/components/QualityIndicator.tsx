import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Info,
  TrendingUp,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';

interface QualityIndicatorProps {
  qualityScore?: number;
  wordCount: number;
  targetWordCount?: number;
  passesCompleted?: number;
  generationTime?: number;
  modelUsed?: string;
  compact?: boolean;
}

const QualityIndicator: React.FC<QualityIndicatorProps> = ({
  qualityScore,
  wordCount,
  targetWordCount,
  passesCompleted,
  generationTime,
  modelUsed,
  compact = false,
}) => {
  const getQualityColor = (score: number) => {
    if (score >= 0.8) return '#22c55e'; // green
    if (score >= 0.6) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const getQualityLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Needs Improvement';
  };

  const getQualityIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle fontSize="small" />;
    if (score >= 0.6) return <TrendingUp fontSize="small" />;
    if (score >= 0.4) return <Warning fontSize="small" />;
    return <Error fontSize="small" />;
  };

  const getWordCountStatus = () => {
    if (!targetWordCount) return 'neutral';
    const ratio = wordCount / targetWordCount;
    if (ratio >= 0.9 && ratio <= 1.1) return 'good';
    if (ratio >= 0.8 && ratio <= 1.2) return 'fair';
    return 'poor';
  };

  const getWordCountColor = (status: string) => {
    switch (status) {
      case 'good': return '#22c55e';
      case 'fair': return '#f59e0b';
      case 'poor': return '#ef4444';
      default: return '#64748b';
    }
  };

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {qualityScore !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {getQualityIcon(qualityScore)}
              <Typography variant="body2" fontWeight={600}>
                {(qualityScore * 100).toFixed(0)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={qualityScore * 100}
              sx={{
                width: 60,
                height: 6,
                borderRadius: 3,
                backgroundColor: '#f1f5f9',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getQualityColor(qualityScore),
                  borderRadius: 3,
                },
              }}
            />
          </Box>
        )}
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography 
            variant="body2" 
            sx={{ 
              color: getWordCountColor(getWordCountStatus()),
              fontWeight: 500,
            }}
          >
            {wordCount.toLocaleString()}
          </Typography>
          {targetWordCount && (
            <Typography variant="caption" color="text.secondary">
              / {targetWordCount.toLocaleString()} words
            </Typography>
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            Quality Metrics
          </Typography>
          <Tooltip title="Quality metrics are calculated based on prose quality, dialogue balance, narrative flow, and consistency">
            <IconButton size="small">
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Quality Score */}
        {qualityScore !== undefined && (
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Overall Quality
              </Typography>
              <Typography variant="h6" fontWeight={700}>
                {(qualityScore * 100).toFixed(0)}%
              </Typography>
            </Box>
            
            <LinearProgress
              variant="determinate"
              value={qualityScore * 100}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: '#f1f5f9',
                mb: 1,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getQualityColor(qualityScore),
                  borderRadius: 4,
                },
              }}
            />
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getQualityIcon(qualityScore)}
              <Chip
                label={getQualityLabel(qualityScore)}
                size="small"
                sx={{
                  backgroundColor: getQualityColor(qualityScore),
                  color: 'white',
                  fontWeight: 500,
                }}
              />
            </Box>
          </Box>
        )}

        {/* Word Count */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="subtitle2" fontWeight={600}>
              Word Count
            </Typography>
            <Typography variant="body1" fontWeight={600}>
              {wordCount.toLocaleString()}
              {targetWordCount && (
                <Typography component="span" variant="body2" color="text.secondary">
                  {' '}/ {targetWordCount.toLocaleString()}
                </Typography>
              )}
            </Typography>
          </Box>
          
          {targetWordCount && (
            <LinearProgress
              variant="determinate"
              value={Math.min((wordCount / targetWordCount) * 100, 100)}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: '#f1f5f9',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getWordCountColor(getWordCountStatus()),
                  borderRadius: 3,
                },
              }}
            />
          )}
        </Box>

        {/* Generation Details */}
        {(passesCompleted || generationTime || modelUsed) && (
          <Box sx={{ pt: 2, borderTop: '1px solid #e2e8f0' }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Generation Details
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {passesCompleted && (
                <Chip
                  label={`${passesCompleted} ${passesCompleted === 1 ? 'Pass' : 'Passes'}`}
                  size="small"
                  variant="outlined"
                  color="primary"
                />
              )}
              
              {generationTime && (
                <Chip
                  label={`${generationTime.toFixed(1)}s`}
                  size="small"
                  variant="outlined"
                  color="secondary"
                />
              )}
              
              {modelUsed && (
                <Chip
                  label={modelUsed}
                  size="small"
                  variant="outlined"
                  color="default"
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default QualityIndicator;