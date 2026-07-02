import React from 'react';
import { FileText, Copy, Check, Download } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResultDisplayProps {
  originalText: string;
  translatedText: string;
  confidence?: number;
}

export default function ResultDisplay({
  originalText,
  translatedText,
  confidence,
}: ResultDisplayProps) {
  const [copiedOriginal, setCopiedOriginal] = React.useState(false);
  const [copiedTranslation, setCopiedTranslation] = React.useState(false);

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

  const downloadResult = () => {
    const content = `原文:\n${originalText}\n\n译文:\n${translatedText}`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'translation_result.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!originalText && !translatedText) {
    return null;
  }

  return (
    <div className="bg-white border rounded-lg shadow-md overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-50 border-b">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-500" />
          <h2 className="font-semibold text-gray-800">翻译结果</h2>
          {confidence && (
            <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
              置信度: {(confidence * 100).toFixed(1)}%
            </span>
          )}
        </div>
        {translatedText && (
          <button
            onClick={downloadResult}
            className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">下载</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
        {/* 原文展示 */}
        <div className="border rounded-lg overflow-hidden">
          <div className="flex items-center justify-between p-3 bg-gray-50 border-b">
            <span className="font-medium text-gray-700">原文</span>
            <button
              onClick={() => copyToClipboard(originalText, 'original')}
              className="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            >
              {copiedOriginal ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
              <span className="text-xs">
                {copiedOriginal ? '已复制' : '复制'}
              </span>
            </button>
          </div>
          <div className="p-4 bg-white min-h-[200px] max-h-[400px] overflow-y-auto">
            <p className="text-gray-800 whitespace-pre-wrap">{originalText}</p>
          </div>
        </div>

        {/* 译文展示 */}
        <div className="border rounded-lg overflow-hidden">
          <div className="flex items-center justify-between p-3 bg-gray-50 border-b">
            <span className="font-medium text-gray-700">译文</span>
            <button
              onClick={() => copyToClipboard(translatedText, 'translation')}
              className="flex items-center gap-1 px-2 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            >
              {copiedTranslation ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
              <span className="text-xs">
                {copiedTranslation ? '已复制' : '复制'}
              </span>
            </button>
          </div>
          <div className="p-4 bg-white min-h-[200px] max-h-[400px] overflow-y-auto">
            <p className="text-gray-800 whitespace-pre-wrap">{translatedText}</p>
          </div>
        </div>
      </div>
    </div>
  );
}