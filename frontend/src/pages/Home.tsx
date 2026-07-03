import React, { useState } from 'react';
import { FileText, Languages, Loader2, Copy, Check, Sparkles, ArrowRight, BookOpen, History } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import RealtimeSubtitle from '@/components/RealtimeSubtitle';
import GlossaryPanel from '@/components/GlossaryPanel';
import MemoryPanel from '@/components/MemoryPanel';
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
  const [isSimulation, setIsSimulation] = useState<boolean>(false);
  const [quickTestText, setQuickTestText] = useState<string>('Hello World');
  const [quickTestResult, setQuickTestResult] = useState<string>('');
  const [isQuickTranslating, setIsQuickTranslating] = useState<boolean>(false);
  const [quickTestSimulation, setQuickTestSimulation] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'translate' | 'glossary' | 'memory'>('translate');

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

      // OCR成功后自动调用翻译接口
      if (ocrResponse.text && ocrResponse.text.trim()) {
        await autoTranslate(ocrResponse.text, sourceLang, targetLang);
      }
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

  const autoTranslate = async (text: string, srcLang: string, tgtLang: string) => {
    if (!text || !text.trim()) return;

    setError('');
    setIsTranslating(true);
    setTranslatedText('');

    try {
      const translateResponse = await translateText(text, srcLang, tgtLang);
      if (!translateResponse.success) {
        throw new Error(translateResponse.message);
      }

      setTranslatedText(translateResponse.translatedText);
      setIsSimulation(translateResponse.simulation || false);
      setIsTranslating(false);
    } catch (err: any) {
      setError('翻译失败: ' + (err.message || '未知错误'));
      setIsTranslating(false);
    }
  };

  const handleTranslate = async () => {
    if (!originalText) return;

    await autoTranslate(originalText, sourceLang, targetLang);
  };

  const handleQuickTranslate = async () => {
    if (!quickTestText.trim()) return;

    setIsQuickTranslating(true);
    setQuickTestResult('');

    try {
      const translateResponse = await translateText(quickTestText, sourceLang, targetLang);
      if (!translateResponse.success) {
        throw new Error(translateResponse.message);
      }

      setQuickTestResult(translateResponse.translatedText);
      setQuickTestSimulation(translateResponse.simulation || false);
      setIsQuickTranslating(false);
    } catch (err: any) {
      setError('快速翻译失败: ' + (err.message || '未知错误'));
      setIsQuickTranslating(false);
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

      {/* 功能导航标签 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab('translate')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'translate'
                  ? 'text-blue-600 border-blue-600 bg-blue-50'
                  : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Sparkles className="w-5 h-5" />
              翻译
            </button>
            <button
              onClick={() => setActiveTab('glossary')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'glossary'
                  ? 'text-purple-600 border-purple-600 bg-purple-50'
                  : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <BookOpen className="w-5 h-5" />
              术语库
            </button>
            <button
              onClick={() => setActiveTab('memory')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'memory'
                  ? 'text-amber-600 border-amber-600 bg-amber-50'
                  : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <History className="w-5 h-5" />
              记忆库
            </button>
          </div>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'translate' && (
          <div className="space-y-6">
            {/* 错误提示 */}
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-start gap-3 shadow-sm">
                <div className="flex-shrink-0 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold">!</div>
                <p className="text-red-700 font-medium flex-1">{error}</p>
                <button
                  onClick={() => setError('')}
                  className="flex-shrink-0 text-red-400 hover:text-red-600 text-xl leading-none"
                >
                  ×
                </button>
              </div>
            )}

          {/* 实时字幕区域 */}
          <RealtimeSubtitle
            sourceLang={sourceLang}
            targetLang={targetLang}
            onSourceLangChange={setSourceLang}
            onTargetLangChange={setTargetLang}
          />

          {/* 快速翻译测试区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-2xl">⚡</span>
              快速翻译测试
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              直接输入文字测试翻译功能，无需上传图片
            </p>
            <div className="flex gap-3">
              <input
                type="text"
                value={quickTestText}
                onChange={(e) => setQuickTestText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleQuickTranslate()}
                placeholder="输入文字，如：Hello World"
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-400 text-base transition-all"
              />
              <button
                onClick={handleQuickTranslate}
                disabled={isQuickTranslating || !quickTestText.trim()}
                className={`
                  flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all transform
                  ${isQuickTranslating || !quickTestText.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-500 to-teal-500 text-white hover:from-green-600 hover:to-teal-600 shadow-lg hover:shadow-xl active:scale-95'
                  }
                `}
              >
                {isQuickTranslating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    翻译中...
                  </>
                ) : (
                  <>
                    <Languages className="w-5 h-5" />
                    立即翻译
                  </>
                )}
              </button>
            </div>
            {quickTestResult && (
              <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-xl border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-semibold text-green-700">翻译结果：</span>
                  {quickTestSimulation && (
                    <span className="text-xs px-2 py-0.5 bg-yellow-400 text-yellow-900 rounded-full font-semibold">
                      模拟模式
                    </span>
                  )}
                </div>
                <p className="text-gray-800 text-lg">{quickTestResult}</p>
              </div>
            )}
          </div>

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
              <div className="p-5 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-b">
                <div className="flex flex-col sm:flex-row items-center gap-4">
                  <div className="flex-1 w-full">
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      源语言
                    </label>
                    <select
                      value={sourceLang}
                      onChange={(e) => setSourceLang(e.target.value)}
                      disabled={isTranslating}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-400 text-base font-medium transition-all bg-white"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center justify-center pt-2 sm:pt-5">
                    <div className="p-3 bg-white rounded-full shadow-md">
                      <ArrowRight className="w-6 h-6 text-blue-500" />
                    </div>
                  </div>

                  <div className="flex-1 w-full">
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      目标语言
                    </label>
                    <select
                      value={targetLang}
                      onChange={(e) => setTargetLang(e.target.value)}
                      disabled={isTranslating}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-400 text-base font-medium transition-all bg-white"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="pt-2 sm:pt-5 w-full sm:w-auto">
                    <button
                      onClick={handleTranslate}
                      disabled={isTranslating || !originalText}
                      className={`
                        w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl font-bold text-lg transition-all transform
                        ${isTranslating || !originalText
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95'
                        }
                      `}
                    >
                      {isTranslating ? (
                        <>
                          <Loader2 className="w-6 h-6 animate-spin" />
                          翻译中...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-6 h-6" />
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
                    <textarea
                      value={originalText}
                      onChange={(e) => setOriginalText(e.target.value)}
                      className="w-full h-full min-h-[180px] text-gray-800 whitespace-pre-wrap resize-none border-0 focus:outline-none bg-transparent"
                      placeholder="识别出的文字会显示在这里，您也可以手动编辑..."
                    />
                  </div>
                </div>

                {/* 译文 */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-100 to-purple-100 border-b">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-blue-700">译文</span>
                      {isSimulation && (
                        <span className="text-xs px-2 py-0.5 bg-yellow-400 text-yellow-900 rounded-full font-semibold">
                          模拟模式
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => translatedText && copyToClipboard(translatedText, 'translation')}
                      disabled={!translatedText}
                      className="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800 hover:bg-blue-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="text-5xl mb-4">👆</div>
              <p className="text-xl font-semibold text-gray-800 mb-2">
                上传一张包含文字的图片开始翻译
              </p>
              <p className="text-gray-500 mb-6">
                支持 JPG、PNG 格式，拖拽或点击上传区域选择图片
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm">
                  <span>📷</span>
                  <span>图片OCR识别</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm">
                  <span>🌐</span>
                  <span>多语言翻译</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm">
                  <span>📝</span>
                  <span>术语表功能</span>
                </div>
              </div>
            </div>
          )}
        </div>
        )}

        {activeTab === 'glossary' && (
          <div className="space-y-6">
            <GlossaryPanel />
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="space-y-6">
            <MemoryPanel />
          </div>
        )}
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