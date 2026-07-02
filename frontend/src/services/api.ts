import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

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