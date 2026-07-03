import axios from 'axios';

const API_BASE_URL = '/api';

export interface UploadResponse {
  success: boolean;
  fileId: string;
  fileName: string;
  filePath: string;
  fileType: string;
  message: string;
}

export interface OCRResponse {
  success: boolean;
  text: string;
  confidence: number;
  message: string;
}

export interface TranslateResponse {
  success: boolean;
  originalText: string;
  translatedText: string;
  sourceLang: string;
  targetLang: string;
  simulation?: boolean;
  glossaryMatches: Array<{
    source_term: string;
    target_term: string;
    id: string;
  }>;
  message: string;
}

export interface SpeechStartResponse {
  success: boolean;
  taskId: string;
  sourceLang: string;
  targetLang: string;
  simulation: boolean;
  message: string;
}

export interface SpeechStopResponse {
  success: boolean;
  message: string;
}

export interface SubtitleResponse {
  success: boolean;
  taskId: string;
  subtitles: Array<{
    type: string;
    task_id: string;
    sentence_index: number;
    original_text: string;
    translated_text: string;
    source_lang: string;
    target_lang: string;
    timestamp: string;
    is_final: boolean;
  }>;
  count: number;
  message: string;
}

// 上传文件
export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<UploadResponse>(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// OCR识别
export const performOCR = async (filePath: string): Promise<OCRResponse> => {
  const response = await axios.post<OCRResponse>(`${API_BASE_URL}/ocr`, {
    filePath,
  });

  return response.data;
};

// 翻译文本
export const translateText = async (
  text: string,
  sourceLang: string,
  targetLang: string
): Promise<TranslateResponse> => {
  const response = await axios.post<TranslateResponse>(`${API_BASE_URL}/translate`, {
    text,
    sourceLang,
    targetLang,
  });

  return response.data;
};

// ==================== 语音翻译API ====================

// 启动实时语音翻译
export const startSpeechTranslation = async (
  sourceLang: string,
  targetLang: string
): Promise<SpeechStartResponse> => {
  const response = await axios.post<SpeechStartResponse>(`${API_BASE_URL}/speech/start`, {
    sourceLang,
    targetLang,
  });

  return response.data;
};

// 停止实时语音翻译
export const stopSpeechTranslation = async (taskId: string): Promise<SpeechStopResponse> => {
  const response = await axios.post<SpeechStopResponse>(`${API_BASE_URL}/speech/stop/${taskId}`);

  return response.data;
};

// 获取字幕历史记录
export const getSubtitles = async (taskId: string): Promise<SubtitleResponse> => {
  const response = await axios.get<SubtitleResponse>(`${API_BASE_URL}/speech/subtitles/${taskId}`);

  return response.data;
};


// ==================== 术语库API ====================

export interface GlossaryTerm {
  id: string;
  source_term: string;
  target_term: string;
  source_lang: string;
  target_lang: string;
  description: string;
  case_sensitive: boolean;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface GlossaryResponse {
  success: boolean;
  glossary: GlossaryTerm[];
  count: number;
  message: string;
}

export interface GlossaryTermResponse {
  success: boolean;
  term: GlossaryTerm;
  message: string;
}

export const getGlossary = async (
  sourceLang?: string,
  targetLang?: string
): Promise<GlossaryResponse> => {
  const params: Record<string, string> = {};
  if (sourceLang) params.sourceLang = sourceLang;
  if (targetLang) params.targetLang = targetLang;

  const response = await axios.get<GlossaryResponse>(`${API_BASE_URL}/glossary`, { params });
  return response.data;
};

export const addGlossaryTerm = async (term: {
  sourceTerm: string;
  targetTerm: string;
  sourceLang: string;
  targetLang: string;
  description?: string;
  caseSensitive?: boolean;
  priority?: number;
}): Promise<GlossaryTermResponse> => {
  const response = await axios.post<GlossaryTermResponse>(`${API_BASE_URL}/glossary`, term);
  return response.data;
};

export const updateGlossaryTerm = async (
  termId: string,
  updates: Partial<{
    sourceTerm: string;
    targetTerm: string;
    sourceLang: string;
    targetLang: string;
    description: string;
    caseSensitive: boolean;
    priority: number;
  }>
): Promise<GlossaryTermResponse> => {
  const response = await axios.put<GlossaryTermResponse>(`${API_BASE_URL}/glossary/${termId}`, updates);
  return response.data;
};

export const deleteGlossaryTerm = async (termId: string): Promise<{ success: boolean; message: string }> => {
  const response = await axios.delete<{ success: boolean; message: string }>(`${API_BASE_URL}/glossary/${termId}`);
  return response.data;
};

export const importGlossary = async (terms: GlossaryTerm[]): Promise<{ success: boolean; importedCount: number; message: string }> => {
  const response = await axios.post<{ success: boolean; importedCount: number; message: string }>(`${API_BASE_URL}/glossary/import`, { terms });
  return response.data;
};

export const exportGlossary = async (sourceLang?: string, targetLang?: string): Promise<GlossaryResponse> => {
  const params: Record<string, string> = {};
  if (sourceLang) params.sourceLang = sourceLang;
  if (targetLang) params.targetLang = targetLang;

  const response = await axios.get<GlossaryResponse>(`${API_BASE_URL}/glossary/export`, { params });
  return response.data;
};


// ==================== 翻译记忆库API ====================

export interface MemoryEntry {
  id: string;
  source_text: string;
  target_text: string;
  source_lang: string;
  target_lang: string;
  confidence: number;
  glossary_matches: GlossaryTerm[];
  created_at: string;
  used_count: number;
  last_used_at: string | null;
}

export interface MemoryResponse {
  success: boolean;
  memory: MemoryEntry[];
  total: number;
  page: number;
  pageSize: number;
  message: string;
}

export interface MemorySearchResponse {
  success: boolean;
  results: (MemoryEntry & { match_score: number })[];
  count: number;
  message: string;
}

export interface MemorySimilarResponse {
  success: boolean;
  found: boolean;
  entry: MemoryEntry | null;
  message: string;
}

export const getMemory = async (
  sourceLang?: string,
  targetLang?: string,
  page: number = 1,
  pageSize: number = 20
): Promise<MemoryResponse> => {
  const params: Record<string, string | number> = { page, pageSize };
  if (sourceLang) params.sourceLang = sourceLang;
  if (targetLang) params.targetLang = targetLang;

  const response = await axios.get<MemoryResponse>(`${API_BASE_URL}/memory`, { params });
  return response.data;
};

export const searchMemory = async (
  query: string,
  sourceLang?: string,
  targetLang?: string,
  maxResults: number = 10
): Promise<MemorySearchResponse> => {
  const params: Record<string, string | number> = { query, maxResults };
  if (sourceLang) params.sourceLang = sourceLang;
  if (targetLang) params.targetLang = targetLang;

  const response = await axios.get<MemorySearchResponse>(`${API_BASE_URL}/memory/search`, { params });
  return response.data;
};

export const getSimilarMemory = async (
  text: string,
  sourceLang: string,
  targetLang: string,
  minConfidence: number = 0.7
): Promise<MemorySimilarResponse> => {
  const response = await axios.post<MemorySimilarResponse>(`${API_BASE_URL}/memory/similar`, {
    text,
    sourceLang,
    targetLang,
    minConfidence
  });
  return response.data;
};

export const getMemoryEntry = async (entryId: string): Promise<{ success: boolean; entry: MemoryEntry; message: string }> => {
  const response = await axios.get<{ success: boolean; entry: MemoryEntry; message: string }>(`${API_BASE_URL}/memory/${entryId}`);
  return response.data;
};

export const updateMemoryEntry = async (
  entryId: string,
  updates: { targetText?: string; confidence?: number }
): Promise<{ success: boolean; entry: MemoryEntry; message: string }> => {
  const response = await axios.put<{ success: boolean; entry: MemoryEntry; message: string }>(`${API_BASE_URL}/memory/${entryId}`, updates);
  return response.data;
};

export const deleteMemoryEntry = async (entryId: string): Promise<{ success: boolean; message: string }> => {
  const response = await axios.delete<{ success: boolean; message: string }>(`${API_BASE_URL}/memory/${entryId}`);
  return response.data;
};

export const exportMemory = async (sourceLang?: string, targetLang?: string): Promise<MemoryResponse> => {
  const params: Record<string, string> = {};
  if (sourceLang) params.sourceLang = sourceLang;
  if (targetLang) params.targetLang = targetLang;

  const response = await axios.get<MemoryResponse>(`${API_BASE_URL}/memory/export`, { params });
  return response.data;
};

export const importMemory = async (entries: MemoryEntry[]): Promise<{ success: boolean; importedCount: number; message: string }> => {
  const response = await axios.post<{ success: boolean; importedCount: number; message: string }>(`${API_BASE_URL}/memory/import`, { entries });
  return response.data;
};

export const clearMemory = async (): Promise<{ success: boolean; clearedCount: number; message: string }> => {
  const response = await axios.post<{ success: boolean; clearedCount: number; message: string }>(`${API_BASE_URL}/memory/clear`);
  return response.data;
};