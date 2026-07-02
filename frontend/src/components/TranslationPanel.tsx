import React from 'react';
import { Languages, ArrowRight, Loader2 } from 'lucide-react';

interface TranslationPanelProps {
  sourceLang: string;
  targetLang: string;
  onSourceLangChange: (lang: string) => void;
  onTargetLangChange: (lang: string) => void;
  onTranslate: () => void;
  isTranslating: boolean;
  hasFile: boolean;
  hasText: boolean;
}

const LANGUAGES = [
  { code: 'en', name: '英文' },
  { code: 'zh', name: '中文' },
  { code: 'ja', name: '日文' },
  { code: 'ko', name: '韩文' },
  { code: 'fr', name: '法文' },
  { code: 'de', name: '德文' },
  { code: 'es', name: '西班牙文' },
  { code: 'ru', name: '俄文' },
];

export default function TranslationPanel({
  sourceLang,
  targetLang,
  onSourceLangChange,
  onTargetLangChange,
  onTranslate,
  isTranslating,
  hasFile,
  hasText,
}: TranslationPanelProps) {
  const canTranslate = hasFile && hasText && !isTranslating;

  return (
    <div className="bg-white border rounded-lg p-6 shadow-md">
      <div className="flex items-center gap-2 mb-6">
        <Languages className="w-6 h-6 text-blue-500" />
        <h2 className="text-lg font-semibold text-gray-800">翻译设置</h2>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 mb-6">
        <div className="flex-1 w-full sm:w-auto">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            源语言
          </label>
          <select
            value={sourceLang}
            onChange={(e) => onSourceLangChange(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={isTranslating}
          >
            {LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center">
          <ArrowRight className="w-6 h-6 text-gray-400" />
        </div>

        <div className="flex-1 w-full sm:w-auto">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            目标语言
          </label>
          <select
            value={targetLang}
            onChange={(e) => onTargetLangChange(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={isTranslating}
          >
            {LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={onTranslate}
        disabled={!canTranslate}
        className={`
          w-full py-4 rounded-lg font-semibold transition-all duration-300
          ${
            canTranslate
              ? 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105 active:scale-95 shadow-lg'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        {isTranslating ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin" />
            翻译中...
          </span>
        ) : (
          '开始翻译'
        )}
      </button>

      {!hasFile && (
        <p className="text-sm text-gray-500 text-center mt-3">
          请先上传文件
        </p>
      )}

      {hasFile && !hasText && (
        <p className="text-sm text-orange-600 text-center mt-3">
          请等待文件识别完成
        </p>
      )}
    </div>
  );
}