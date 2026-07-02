import React, { useState } from 'react';
import { FileText, Languages, Loader2, Copy, Check } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import RealtimeSubtitle from '@/components/RealtimeSubtitle';
import { uploadFile, performOCR, translateText } from '@/services/api';

const LANGUAGES = [
  { code: 'en', name: '英文' },
  { code: 'zh', name: '中文' },
  { code: 'ja', name: '日文' },
  { code: 'ko', name: '韩文' },
  { code: 'fr', name: '法文' },
  { code: 'de', name: '德文' },
];

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
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedTranslation, setCopiedTranslation] = useState(false);

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setError('');
    setIsUploading(true);
    setOriginalText('');
    setTranslatedText('');
    setConfidence(0);

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
    setTranslatedText('');

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

  const copyToClipboard = async (text: string, type: 'original' | 'translation') => {
    await navigator.clipboard.writeText(text);
    if (type === 'original') {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    } else {
      setCopiedTranslation(true);
      setTimeout(() => setCopiedTranslation(false), 2000);
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
              第一步：上传图片
            </h2>
            <FileUpload
              onFileUpload={handleFileUpload}
              uploadedFile={uploadedFile}
              onClearFile={handleClearFile}
              isUploading={isUploading}
            />
            {isRecognizing && (
              <div className="mt-4 flex items-center justify-center gap-2 text-blue-600">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>正在识别图片中的文字...</span>
              </div>
            )}
          </div>

          {/* OCR识别结果 + 翻译区域 */}
          {originalText && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              {/* 头部 */}
              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b">
                <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                  <span className="text-2xl">📝</span>
                  第二步：翻译文字
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  已识别出文字，请选择语言后点击翻译按钮
                </p>
              </div>

              {/* 语言选择 + 翻译按钮 */}
              <div className="p-4 bg-gray-50 border-b">
                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <div className="flex-1 w-full">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      源语言
                    </label>
                    <select
                      value={sourceLang}
                      onChange={(e) => setSourceLang(e.target.value)}
                      disabled={isTranslating}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center justify-center pt-5">
                    <span className="text-2xl text-gray-400">→</span>
                  </div>

                  <div className="flex-1 w-full">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      目标语言
                    </label>
                    <select
                      value={targetLang}
                      onChange={(e) => setTargetLang(e.target.value)}
                      disabled={isTranslating}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="pt-5">
                    <button
                      onClick={handleTranslate}
                      disabled={isTranslating || !originalText}
                      className={`
                        flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold transition-all
                        ${isTranslating || !originalText
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl active:scale-95'
                        }
                      `}
                    >
                      {isTranslating ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          翻译中...
                        </>
                      ) : (
                        <>
                          <Languages className="w-5 h-5" />
                          开始翻译
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* 原文 + 译文 对比展示 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
                {/* 原文 */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between p-3 bg-gray-100 border-b">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700">原文</span>
                      {confidence > 0 && (
                        <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                          识别度 {(confidence * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => copyToClipboard(originalText, 'original')}
                      className="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
                    >
                      {copiedOriginal ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                      <span className="text-xs">{copiedOriginal ? '已复制' : '复制'}</span>
                    </button>
                  </div>
                  <div className="p-4 bg-white min-h-[200px] max-h-[400px] overflow-y-auto">
                    <p className="text-gray-800 whitespace-pre-wrap">{originalText}</p>
                  </div>
                </div>

                {/* 译文 */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between p-3 bg-blue-50 border-b">
                    <span className="font-medium text-blue-700">译文</span>
                    <button
                      onClick={() => translatedText && copyToClipboard(translatedText, 'translation')}
                      disabled={!translatedText}
                      className="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800 hover:bg-blue-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {copiedTranslation ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                      <span className="text-xs">{copiedTranslation ? '已复制' : '复制'}</span>
                    </button>
                  </div>
                  <div className="p-4 bg-white min-h-[200px] max-h-[400px] overflow-y-auto">
                    {isTranslating ? (
                      <div className="flex items-center justify-center h-full text-gray-400">
                        <Loader2 className="w-6 h-6 animate-spin mr-2" />
                        <span>正在翻译...</span>
                      </div>
                    ) : translatedText ? (
                      <p className="text-gray-800 whitespace-pre-wrap">{translatedText}</p>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-400">
                        <p>点击「开始翻译」按钮获取译文</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 上传提示 */}
          {!uploadedFile && !isRecognizing && (
            <div className="text-center text-gray-500 py-8">
              <p className="text-lg">👆 上传一张包含文字的图片开始翻译</p>
            </div>
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