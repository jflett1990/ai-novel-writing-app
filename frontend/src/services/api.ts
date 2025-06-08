import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('Making API request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      data: config.data,
    });
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('API response:', {
      status: response.status,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.error('Response error:', {
      message: error.message,
      code: error.code,
      config: error.config,
      response: error.response,
    });
    return Promise.reject(error);
  }
);

// Types
export interface Story {
  story_id: number;
  title: string;
  description?: string;
  genre?: string;
  target_word_count: number;
  target_chapters: number;
  created_at: string;
  updated_at?: string;
  acts?: Act[];
  chapters?: Chapter[];
  character_count?: number;
  world_element_count?: number;
  total_word_count?: number;
}

export interface Act {
  act_id: number;
  number: number;
  title?: string;
  summary?: string;
}

export interface Chapter {
  chapter_id: number;
  number: number;
  title?: string;
  summary?: string;
  content?: string;
  is_generated: boolean;
  is_approved: boolean;
  word_count: number;
  act_id?: number;
  created_at: string;
  updated_at?: string;
  quality_score?: number; // Enhanced: Quality score from 0-1
}

export interface Character {
  character_id: number;
  story_id: number;
  name: string;
  role?: string;
  profile?: string;
  traits?: any;
  arc?: string;
  appearance?: string;
  personality?: string;
  background?: string;
  motivations?: string;
}

export interface WorldElement {
  element_id: number;
  story_id: number;
  type: string;
  name: string;
  description?: string;
  meta?: any;
  category?: string;
  importance?: string;
}

export interface CreateStoryRequest {
  title: string;
  description?: string;
  genre?: string;
  target_chapters?: number;
  target_word_count?: number;
}

export interface GenerateOutlineRequest {
  target_chapters?: number;
  custom_prompt?: string;
}

export interface GenerateCharactersRequest {
  character_count?: number;
  custom_prompt?: string;
}

// Enhanced generation types
export type GenerationMode = 'standard' | 'enhanced';

export interface EnhancedGenerationRequest {
  target_word_count?: number;
  quality_check?: boolean;
  custom_prompt?: string;
}

export interface EnhancedGenerationResponse {
  success: boolean;
  chapter_content?: string;
  word_count?: number;
  quality_score?: number;
  passes_completed?: number;
  generation_time?: number;
  model_used?: string;
  tokens_used?: number;
  error?: string;
  error_type?: string;
}

export interface MultiPassGenerationResponse {
  success: boolean;
  chapter_content?: string;
  word_count?: number;
  quality_score?: number;
  passes_completed: number;
  generation_time?: number;
  model_used?: string;
  tokens_used?: number;
  improvement_notes?: string[];
  error?: string;
  error_type?: string;
}

export interface QualityAnalysisResponse {
  quality_score: number;
  word_count: number;
  paragraph_count: number;
  dialogue_count: number;
  issues: string[];
  suggestions: string[];
  style_consistency?: number;
  readability_score?: number;
}

export interface FeatureAvailabilityResponse {
  enhanced_generation: boolean;
  multi_pass_generation: boolean;
  quality_analysis: boolean;
  custom_prompting: boolean;
}

// API Functions
export const storyApi = {
  // Stories
  getStories: async (): Promise<Story[]> => {
    const response = await api.get('/api/v1/stories/');
    return response.data;
  },

  getStory: async (id: number): Promise<Story> => {
    const response = await api.get(`/api/v1/stories/${id}`);
    return response.data;
  },

  createStory: async (data: CreateStoryRequest): Promise<Story> => {
    const response = await api.post('/api/v1/stories/', data);
    return response.data;
  },

  updateStory: async (id: number, data: Partial<CreateStoryRequest>): Promise<Story> => {
    const response = await api.put(`/api/v1/stories/${id}`, data);
    return response.data;
  },

  deleteStory: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/stories/${id}`);
  },

  // Chapters
  getChapter: async (storyId: number, chapterNumber: number): Promise<Chapter> => {
    const response = await api.get(`/api/v1/stories/${storyId}/chapters/${chapterNumber}`);
    return response.data;
  },

  updateChapter: async (storyId: number, chapterNumber: number, data: Partial<Chapter>): Promise<Chapter> => {
    const response = await api.put(`/api/v1/stories/${storyId}/chapters/${chapterNumber}`, data);
    return response.data;
  },

  // Characters
  getCharacters: async (storyId: number): Promise<Character[]> => {
    const response = await api.get(`/api/v1/characters/story/${storyId}`);
    return response.data;
  },

  createCharacter: async (storyId: number, data: Omit<Character, 'character_id' | 'story_id'>): Promise<Character> => {
    const response = await api.post(`/api/v1/characters/story/${storyId}`, data);
    return response.data;
  },

  updateCharacter: async (characterId: number, data: Partial<Character>): Promise<Character> => {
    const response = await api.put(`/api/v1/characters/${characterId}`, data);
    return response.data;
  },

  deleteCharacter: async (characterId: number): Promise<void> => {
    await api.delete(`/api/v1/characters/${characterId}`);
  },

  // World Elements
  getWorldElements: async (storyId: number): Promise<WorldElement[]> => {
    const response = await api.get(`/api/v1/world/story/${storyId}`);
    return response.data;
  },

  createWorldElement: async (storyId: number, data: Omit<WorldElement, 'element_id' | 'story_id'>): Promise<WorldElement> => {
    const response = await api.post(`/api/v1/world/story/${storyId}`, data);
    return response.data;
  },

  updateWorldElement: async (elementId: number, data: Partial<WorldElement>): Promise<WorldElement> => {
    const response = await api.put(`/api/v1/world/${elementId}`, data);
    return response.data;
  },

  deleteWorldElement: async (elementId: number): Promise<void> => {
    await api.delete(`/api/v1/world/${elementId}`);
  },
};

export interface ChapterExpandRequest {
  expansion_type?: 'enhance' | 'lengthen' | 'detail' | 'prose';
  custom_prompt?: string;
  target_length?: number;
}

export interface ChapterExpandResponse {
  success: boolean;
  expanded_content?: string;
  original_word_count?: number;
  expanded_word_count?: number;
  tokens_used?: number;
  model_used?: string;
  error?: string;
  error_type?: string;
}

export const generationApi = {
  // Check feature availability
  getFeatures: async (): Promise<FeatureAvailabilityResponse> => {
    try {
      const response = await api.get('/api/v1/features');
      return response.data;
    } catch (error) {
      // Fallback to all false if endpoint doesn't exist
      console.warn('Features endpoint not available, using fallback');
      return {
        enhanced_generation: false,
        multi_pass_generation: false,
        quality_analysis: false,
        custom_prompting: false,
      };
    }
  },

  // Generate outline
  generateOutline: async (storyId: number, data: GenerateOutlineRequest): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/outline`, data);
    return response.data;
  },

  // Standard chapter generation (backward compatible)
  generateChapter: async (storyId: number, chapterNumber: number, customPrompt?: string): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/chapters/${chapterNumber}`, {
      custom_prompt: customPrompt,
    });
    return response.data;
  },

  // Enhanced chapter generation
  generateChapterEnhanced: async (
    storyId: number, 
    chapterNumber: number, 
    data: EnhancedGenerationRequest
  ): Promise<EnhancedGenerationResponse> => {
    try {
      const response = await api.post(
        `/api/v1/generate-enhanced/stories/${storyId}/chapters/${chapterNumber}`, 
        data
      );
      return response.data;
    } catch (error) {
      // Fallback to standard generation if enhanced endpoint doesn't exist
      console.warn('Enhanced generation not available, falling back to standard');
      const standardResult = await generationApi.generateChapter(storyId, chapterNumber, data.custom_prompt);
      return {
        success: standardResult.success || false,
        chapter_content: standardResult.chapter_content,
        word_count: standardResult.word_count,
        quality_score: undefined,
        passes_completed: 1,
        generation_time: undefined,
        model_used: standardResult.model_used,
        tokens_used: standardResult.tokens_used,
        error: standardResult.error,
        error_type: standardResult.error_type,
      };
    }
  },

  // Multi-pass chapter generation
  generateChapterMultiPass: async (
    storyId: number, 
    chapterNumber: number, 
    data: EnhancedGenerationRequest
  ): Promise<MultiPassGenerationResponse> => {
    try {
      const response = await api.post(
        `/api/v1/generate-enhanced/stories/${storyId}/chapters/${chapterNumber}/multi-pass`, 
        data
      );
      return response.data;
    } catch (error) {
      console.warn('Multi-pass generation not available, falling back to enhanced');
      // Fallback to enhanced generation
      const enhancedResult = await generationApi.generateChapterEnhanced(storyId, chapterNumber, data);
      return {
        ...enhancedResult,
        passes_completed: 1,
        improvement_notes: [],
      };
    }
  },

  // Chapter quality analysis
  analyzeChapterQuality: async (
    storyId: number, 
    chapterNumber: number
  ): Promise<QualityAnalysisResponse> => {
    try {
      const response = await api.post(
        `/api/v1/generate-enhanced/stories/${storyId}/chapters/${chapterNumber}/analyze-quality`
      );
      return response.data;
    } catch (error) {
      console.warn('Quality analysis not available');
      // Return mock data for now
      return {
        quality_score: 0.75,
        word_count: 2500,
        paragraph_count: 15,
        dialogue_count: 8,
        issues: ['Quality analysis not available - backend enhancement needed'],
        suggestions: ['Enable enhanced backend features for detailed analysis'],
        style_consistency: 0.75,
        readability_score: 0.8,
      };
    }
  },

  // Expand chapter (existing functionality)
  expandChapter: async (storyId: number, chapterNumber: number, data: ChapterExpandRequest): Promise<ChapterExpandResponse> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/chapters/${chapterNumber}/expand`, data);
    return response.data;
  },

  // Generate characters
  generateCharacters: async (storyId: number, data: GenerateCharactersRequest): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/characters`, data);
    return response.data;
  },

  // Generate world elements
  generateWorldElements: async (storyId: number, elementCount: number = 8): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/world?element_count=${elementCount}`);
    return response.data;
  },

  // Check AI provider status
  getProviderStatus: async (): Promise<any> => {
    const response = await api.get('/api/v1/generate/providers/status');
    return response.data;
  },

  // Get complexity setting
  getComplexity: async (): Promise<any> => {
    const response = await api.get('/api/v1/generate/complexity');
    return response.data;
  },

  // Set complexity level
  setComplexity: async (level: string): Promise<any> => {
    const response = await api.post(`/api/v1/generate/complexity/${level}`);
    return response.data;
  },
};

export default api;