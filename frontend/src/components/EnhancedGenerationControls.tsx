import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
  Slider,
  Switch,
  Typography,
  Collapse,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  AutoAwesome,
  Speed,
  HighQuality,
  Tune,
} from '@mui/icons-material';
import { GenerationMode, FeatureAvailabilityResponse } from '../services/api';

interface EnhancedGenerationControlsProps {
  generationMode: GenerationMode;
  onGenerationModeChange: (mode: GenerationMode) => void;
  targetWordCount: number;
  onTargetWordCountChange: (count: number) => void;
  qualityCheck: boolean;
  onQualityCheckChange: (enabled: boolean) => void;
  enhancedAvailable: boolean;
  loading?: boolean;
  qualityScore?: number;
}

const EnhancedGenerationControls: React.FC<EnhancedGenerationControlsProps> = ({
  generationMode,
  onGenerationModeChange,
  targetWordCount,
  onTargetWordCountChange,
  qualityCheck,
  onQualityCheckChange,
  enhancedAvailable,
  loading = false,
  qualityScore,
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

  return (
    <Card 
      sx={{ 
        mb: 3,
        border: generationMode === 'enhanced' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
        background: generationMode === 'enhanced' 
          ? 'linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%)' 
          : 'white'
      }}
    >
      <CardContent>
        <FormControl component="fieldset" fullWidth>
          <FormLabel component="legend" sx={{ mb: 2, fontWeight: 600 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tune fontSize="small" />
              Generation Mode
            </Box>
          </FormLabel>
          
          <RadioGroup
            value={generationMode}
            onChange={(e) => onGenerationModeChange(e.target.value as GenerationMode)}
            sx={{ gap: 1 }}
          >
            <FormControlLabel
              value="standard"
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Speed fontSize="small" />
                  <Box>
                    <Typography variant="body1" fontWeight={500}>
                      Standard Generation
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Fast generation with basic quality
                    </Typography>
                  </Box>
                </Box>
              }
            />
            
            <FormControlLabel
              value="enhanced"
              control={<Radio />}
              disabled={!enhancedAvailable}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <HighQuality fontSize="small" />
                  <Box>
                    <Typography variant="body1" fontWeight={500}>
                      Enhanced Generation
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Higher quality with advanced prompting
                    </Typography>
                  </Box>
                  {!enhancedAvailable && (
                    <Chip 
                      label="Unavailable" 
                      size="small" 
                      color="warning"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>

        <Collapse in={generationMode === 'enhanced' && enhancedAvailable}>
          <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #e2e8f0' }}>
            {/* Target Word Count Slider */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                Target Word Count: {targetWordCount.toLocaleString()}
              </Typography>
              <Slider
                value={targetWordCount}
                onChange={(_, value) => onTargetWordCountChange(value as number)}
                min={1500}
                max={5000}
                step={250}
                marks={[
                  { value: 1500, label: '1.5k' },
                  { value: 2500, label: '2.5k' },
                  { value: 3500, label: '3.5k' },
                  { value: 5000, label: '5k' },
                ]}
                valueLabelDisplay="auto"
                sx={{
                  '& .MuiSlider-thumb': {
                    backgroundColor: '#3b82f6',
                  },
                  '& .MuiSlider-track': {
                    backgroundColor: '#3b82f6',
                  },
                }}
              />
              <Typography variant="caption" color="text.secondary">
                Recommended: 2,000-3,000 words for standard chapters
              </Typography>
            </Box>

            {/* Quality Check Toggle */}
            <Box sx={{ mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={qualityCheck}
                    onChange={(e) => onQualityCheckChange(e.target.checked)}
                    color="primary"
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2" fontWeight={500}>
                      Enable Quality Assessment & Auto-Regeneration
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Automatically analyze and improve content quality
                    </Typography>
                  </Box>
                }
              />
            </Box>

            {/* Current Quality Score Display */}
            {qualityScore !== undefined && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom fontWeight={600}>
                  Current Quality Score
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={qualityScore * 100}
                    sx={{
                      flexGrow: 1,
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#f1f5f9',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getQualityColor(qualityScore),
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="body2" fontWeight={600}>
                    {(qualityScore * 100).toFixed(0)}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={getQualityLabel(qualityScore)}
                    size="small"
                    sx={{
                      backgroundColor: getQualityColor(qualityScore),
                      color: 'white',
                      fontWeight: 500,
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    Based on prose quality, dialogue, and narrative flow
                  </Typography>
                </Box>
              </Box>
            )}

            {/* Loading State */}
            {loading && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress 
                  sx={{ 
                    borderRadius: 4,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#3b82f6',
                    },
                  }} 
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {generationMode === 'enhanced' 
                    ? 'Generating with enhanced quality controls...' 
                    : 'Generating content...'
                  }
                </Typography>
              </Box>
            )}
          </Box>
        </Collapse>

        {/* Feature Unavailable Message */}
        {generationMode === 'enhanced' && !enhancedAvailable && (
          <Box sx={{ mt: 2, p: 2, backgroundColor: '#fef3c7', borderRadius: 1 }}>
            <Typography variant="body2" color="#92400e">
              <strong>Enhanced generation is currently unavailable.</strong> 
              This feature requires the backend enhanced prompting system to be enabled.
              You can still use standard generation.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default EnhancedGenerationControls;