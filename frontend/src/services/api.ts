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

export const generationApi = {
  // Generate outline
  generateOutline: async (storyId: number, data: GenerateOutlineRequest): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/outline`, data);
    return response.data;
  },

  // Generate chapter
  generateChapter: async (storyId: number, chapterNumber: number, customPrompt?: string): Promise<any> => {
    const response = await api.post(`/api/v1/generate/stories/${storyId}/chapters/${chapterNumber}`, {
      custom_prompt: customPrompt,
    });
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
