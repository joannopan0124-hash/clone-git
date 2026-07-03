import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Play, Square, Volume2 } from 'lucide-react';
import { startSpeechTranslation, stopSpeechTranslation, getSubtitles } from '@/services/api';

interface Subtitle {
  type: string;
  task_id: string;
  sentence_index: number;
  original_text: string;
  translated_text: string;
  source_lang: string;
  target_lang: string;
  timestamp: string;
  is_final: boolean;
}

interface RealtimeSubtitleProps {
  sourceLang: string;
  targetLang: string;
  onSourceLangChange: (lang: string) => void;
  onTargetLangChange: (lang: string) => void;
}

export default function RealtimeSubtitle({
  sourceLang,
  targetLang,
  onSourceLangChange,
  onTargetLangChange
}: RealtimeSubtitleProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [taskId, setTaskId] = useState<string>('');
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [currentSubtitle, setCurrentSubtitle] = useState<Subtitle | null>(null);
  const [isSimulation, setIsSimulation] = useState(false);
  const [error, setError] = useState<string>('');

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const languages = [
    { code: 'zh', name: '中文' },
    { code: 'en', name: '英语' },
    { code: 'ja', name: '日语' },
    { code: 'ko', name: '韩语' },
    { code: 'de', name: '德语' },
    { code: 'fr', name: '法语' },
  ];

  const handleStart = async () => {
    setError('');
    try {
      const response = await startSpeechTranslation(sourceLang, targetLang);
      if (!response.success) {
        throw new Error(response.message);
      }

      setTaskId(response.taskId);
      setIsRunning(true);
      setIsSimulation(response.simulation || false);
      setSubtitles([]);
      setCurrentSubtitle(null);

      pollingIntervalRef.current = setInterval(async () => {
        try {
          const subtitleResponse = await getSubtitles(response.taskId);
          if (subtitleResponse.success && subtitleResponse.subtitles) {
            setSubtitles(subtitleResponse.subtitles);
            if (subtitleResponse.subtitles.length > 0) {
              setCurrentSubtitle(subtitleResponse.subtitles[subtitleResponse.subtitles.length - 1]);
            }
          }
        } catch (err) {
          console.error('获取字幕失败:', err);
        }
      }, 1000);
    } catch (err: any) {
      setError(err.message || '启动实时字幕失败');
    }
  };

  const handleStop = async () => {
    if (!taskId) return;

    try {
      const response = await stopSpeechTranslation(taskId);
      if (!response.success) {
        throw new Error(response.message);
      }

      setIsRunning(false);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    } catch (err: any) {
      setError(err.message || '停止实时字幕失败');
    }
  };

  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 font-[楷体]">
          <span className="text-2xl">🎙️</span>
          实时字幕
          {isSimulation && (
            <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
              模拟模式
            </span>
          )}
        </h2>
        <div className="flex items-center gap-2">
          {!isRunning ? (
            <button
              onClick={handleStart}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-black text-white hover:bg-gray-800 rounded-lg transition-colors font-[楷体]"
            >
              <Play className="w-4 h-4" />
              开始
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-black text-white hover:bg-gray-800 rounded-lg transition-colors font-[楷体]"
            >
              <Square className="w-4 h-4" />
              停止
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 font-[楷体]">
            源语言
          </label>
          <select
            value={sourceLang}
            onChange={(e) => onSourceLangChange(e.target.value)}
            disabled={isRunning}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 font-[楷体]"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1 font-[楷体]">
            目标语言
          </label>
          <select
            value={targetLang}
            onChange={(e) => onTargetLangChange(e.target.value)}
            disabled={isRunning}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 font-[楷体]"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 两个框显示原文和译文 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        {/* 原文框 */}
        <div className="border-2 border-gray-300 rounded-lg p-4 min-h-[150px] bg-gray-50">
          <div className="flex items-center gap-2 mb-3">
            {isRunning ? (
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-75"></span>
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse delay-150"></span>
              </div>
            ) : (
              <MicOff className="w-4 h-4 text-gray-400" />
            )}
            <span className="font-bold text-gray-700 font-[楷体]">原文</span>
          </div>
          <div className="text-lg text-gray-800 font-[楷体] min-h-[100px]">
            {currentSubtitle ? (
              <p>{currentSubtitle.original_text}</p>
            ) : isRunning ? (
              <p className="text-gray-400">等待语音输入...</p>
            ) : (
              <p className="text-gray-400">点击开始按钮启动</p>
            )}
          </div>
        </div>

        {/* 译文框 */}
        <div className="border-2 border-blue-300 rounded-lg p-4 min-h-[150px] bg-blue-50">
          <div className="flex items-center gap-2 mb-3">
            {isRunning ? (
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75"></span>
                <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150"></span>
              </div>
            ) : (
              <Volume2 className="w-4 h-4 text-gray-400" />
            )}
            <span className="font-bold text-blue-700 font-[楷体]">译文</span>
          </div>
          <div className="text-lg text-gray-800 font-[楷体] min-h-[100px]">
            {currentSubtitle ? (
              <p>{currentSubtitle.translated_text}</p>
            ) : isRunning ? (
              <p className="text-gray-400">等待翻译结果...</p>
            ) : (
              <p className="text-gray-400">点击开始按钮启动</p>
            )}
          </div>
        </div>
      </div>

      {subtitles.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2 font-[楷体]">
            <Volume2 className="w-4 h-4" />
            字幕历史 ({subtitles.length}条)
          </h3>
          <div className="max-h-[200px] overflow-y-auto space-y-2 bg-gray-50 rounded-lg p-3">
            {subtitles.map((subtitle, index) => (
              <div
                key={index}
                className="p-2 bg-white rounded border border-gray-200 text-sm"
              >
                <div className="text-gray-800 font-[楷体]">{subtitle.original_text}</div>
                <div className="text-blue-600 mt-1 font-[楷体]">{subtitle.translated_text}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isRunning && (
        <div className="mt-4 flex items-center justify-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="font-[楷体]">任务运行中</span>
          </div>
          <div className="flex items-center gap-1">
            <Mic className="w-4 h-4 text-green-500" />
            <span className="font-[楷体]">语音识别</span>
          </div>
        </div>
      )}
    </div>
  );
}
