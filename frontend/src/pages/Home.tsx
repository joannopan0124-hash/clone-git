import React, { useState } from 'react';
import { FileText } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import TranslationPanel from '@/components/TranslationPanel';
import ResultDisplay from '@/components/ResultDisplay';
import RealtimeSubtitle from '@/components/RealtimeSubtitle';
import { uploadFile, performOCR, translateText } from '@/services/api';

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [filePath, setFilePath] = useState<string>('');
  const [originalText, setOriginalText] = useState<string>('');
  const [translatedText, setTranslatedText] = useState<string>('');
  const [confidence, setConfidence] = useState<number>(0);
  const [sourceLang, setSourceLang] = useState<string>('en');
  const [targetLang, setTargetLang] = useState<string>('zh');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isRecognizing, setIsRecognizing] = useState<boolean>(false);
  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setError('');
    setIsUploading(true);

    try {
      // 上传文件
      const uploadResponse = await uploadFile(file);
      if (!uploadResponse.success) {
        throw new Error(uploadResponse.message);
      }

      setFilePath(uploadResponse.filePath);
      setIsUploading(false);
      setIsRecognizing(true);

      // OCR识别
      const ocrResponse = await performOCR(uploadResponse.filePath);
      if (!ocrResponse.success) {
        throw new Error(ocrResponse.message);
      }

      setOriginalText(ocrResponse.text);
      setConfidence(ocrResponse.confidence);
      setIsRecognizing(false);
    } catch (err: any) {
      setError(err.message || '处理文件时出错');
      setIsUploading(false);
      setIsRecognizing(false);
      // 保留上传文件状态，方便用户查看错误信息
    }
  };

  const handleClearFile = () => {
    setUploadedFile(null);
    setFilePath('');
    setOriginalText('');
    setTranslatedText('');
    setConfidence(0);
    setError('');
  };

  const handleTranslate = async () => {
    if (!originalText) return;

    setError('');
    setIsTranslating(true);

    try {
      const translateResponse = await translateText(originalText, sourceLang, targetLang);
      if (!translateResponse.success) {
        throw new Error(translateResponse.message);
      }

      setTranslatedText(translateResponse.translatedText);
      setIsTranslating(false);
    } catch (err: any) {
      setError(err.message || '翻译时出错');
      setIsTranslating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">文档翻译系统</h1>
                <p className="text-sm text-gray-500">支持图片/PDF翻译 + 实时语音字幕</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* 错误提示 */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 font-medium">{error}</p>
            </div>
          )}

          {/* 实时字幕区域 */}
          <RealtimeSubtitle
            sourceLang={sourceLang}
            targetLang={targetLang}
            onSourceLangChange={setSourceLang}
            onTargetLangChange={setTargetLang}
          />

          {/* 文件上传区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">📤</span>
              上传文件
            </h2>
            <FileUpload
              onFileUpload={handleFileUpload}
              uploadedFile={uploadedFile}
              onClearFile={handleClearFile}
              isUploading={isUploading}
            />
            {isRecognizing && (
              <div className="mt-4 flex items-center justify-center gap-2 text-blue-600">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <span>正在识别文件内容...</span>
              </div>
            )}
          </div>

          {/* 翻译面板 */}
          {uploadedFile && originalText && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <TranslationPanel
                sourceLang={sourceLang}
                targetLang={targetLang}
                onSourceLangChange={setSourceLang}
                onTargetLangChange={setTargetLang}
                onTranslate={handleTranslate}
                isTranslating={isTranslating}
                hasFile={!!uploadedFile}
                hasText={!!originalText}
              />
            </div>
          )}

          {/* 结果展示 */}
          {originalText && translatedText && (
            <ResultDisplay
              originalText={originalText}
              translatedText={translatedText}
              confidence={confidence}
            />
          )}
        </div>
      </main>

      {/* 底部 */}
      <footer className="bg-gray-50 border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            文档翻译系统 © 2026 - 支持图片/PDF翻译 + 实时语音字幕
          </p>
        </div>
      </footer>
    </div>
  );
}