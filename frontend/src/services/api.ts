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