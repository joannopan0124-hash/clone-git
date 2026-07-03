import React, { useState, useEffect } from 'react';
import { History, Search, Download, Upload, Trash2, Edit2, Save, X, RefreshCw, Copy, Check, ChevronLeft, ChevronRight } from 'lucide-react';
import { getMemory, searchMemory, updateMemoryEntry, deleteMemoryEntry, exportMemory, importMemory, clearMemory, MemoryEntry } from '@/services/api';

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

export default function MemoryPanel() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceLangFilter, setSourceLangFilter] = useState('');
  const [targetLangFilter, setTargetLangFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize] = useState(20);
  const [editingEntry, setEditingEntry] = useState<MemoryEntry | null>(null);
  const [editingTargetText, setEditingTargetText] = useState('');
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const response = await getMemory(sourceLangFilter || undefined, targetLangFilter || undefined, currentPage, pageSize);
      setEntries(response.memory);
      setTotal(response.total);
    } catch (error) {
      setNotification({ type: 'error', message: '加载记忆库失败' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEntries();
  }, [sourceLangFilter, targetLangFilter, currentPage, pageSize]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadEntries();
      return;
    }

    setLoading(true);
    try {
      const response = await searchMemory(searchQuery, sourceLangFilter || undefined, targetLangFilter || undefined, pageSize);
      setEntries(response.results);
      setTotal(response.count);
    } catch (error) {
      setNotification({ type: 'error', message: '搜索失败' });
    } finally {
      setLoading(false);
    }
  };

  const handleEditEntry = (entry: MemoryEntry) => {
    setEditingEntry(entry);
    setEditingTargetText(entry.target_text);
  };

  const handleUpdateEntry = async () => {
    if (!editingEntry || !editingTargetText.trim()) {
      setNotification({ type: 'error', message: '请填写译文' });
      return;
    }

    try {
      await updateMemoryEntry(editingEntry.id, { targetText: editingTargetText });
      setNotification({ type: 'success', message: '更新成功' });
      setEditingEntry(null);
      setEditingTargetText('');
      loadEntries();
    } catch (error) {
      setNotification({ type: 'error', message: '更新失败' });
    }
  };

  const handleDeleteEntry = async (entryId: string) => {
    if (!confirm('确定要删除这条翻译记录吗？')) return;

    try {
      await deleteMemoryEntry(entryId);
      setNotification({ type: 'success', message: '删除成功' });
      loadEntries();
    } catch (error) {
      setNotification({ type: 'error', message: '删除失败' });
    }
  };

  const handleExport = async () => {
    try {
      const response = await exportMemory(sourceLangFilter || undefined, targetLangFilter || undefined);
      const dataStr = JSON.stringify(response.memory, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'translation_memory.json';
      a.click();
      URL.revokeObjectURL(url);
      setNotification({ type: 'success', message: '导出成功' });
    } catch (error) {
      setNotification({ type: 'error', message: '导出失败' });
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const entriesData = JSON.parse(text);
      await importMemory(entriesData);
      setNotification({ type: 'success', message: '导入成功' });
      loadEntries();
    } catch (error) {
      setNotification({ type: 'error', message: '导入失败，请确保文件格式正确' });
    }
  };

  const handleClear = async () => {
    if (!confirm('确定要清空所有翻译记录吗？此操作不可恢复！')) return;

    try {
      await clearMemory();
      setNotification({ type: 'success', message: '已清空所有记录' });
      loadEntries();
    } catch (error) {
      setNotification({ type: 'error', message: '清空失败' });
    }
  };

  const copyToClipboard = async (text: string, entryId: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(entryId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredEntries = searchQuery ? entries : entries;

  const totalPages = Math.ceil(total / pageSize);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-6 h-6 text-amber-600" />
            <h2 className="text-lg font-semibold text-gray-800">翻译记忆库</h2>
            <span className="text-xs px-2 py-0.5 bg-amber-200 text-amber-700 rounded-full">
              {total} 条记录
            </span>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
              <Upload className="w-4 h-4" />
              <span className="text-sm font-medium">导入</span>
              <input type="file" accept=".json" onChange={handleImport} className="hidden" />
            </label>
            <button
              onClick={handleExport}
              className="flex items-center gap-1 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">导出</span>
            </button>
            <button
              onClick={handleClear}
              className="flex items-center gap-1 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
              title="清空所有记录"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="搜索翻译记录..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-400"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors whitespace-nowrap"
          >
            搜索
          </button>
          <div className="flex gap-3">
            <select
              value={sourceLangFilter}
              onChange={(e) => setSourceLangFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-400 bg-white"
            >
              <option value="">全部源语言</option>
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
            <select
              value={targetLangFilter}
              onChange={(e) => setTargetLangFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-400 bg-white"
            >
              <option value="">全部目标语言</option>
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="max-h-[600px] overflow-y-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">原文</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">译文</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">语言</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">使用次数</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">时间</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  加载中...
                </td>
              </tr>
            ) : filteredEntries.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  {searchQuery ? '未找到匹配的记录' : '暂无翻译记录，进行翻译后自动保存'}
                </td>
              </tr>
            ) : (
              filteredEntries.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 max-w-xs">
                    <div className="text-gray-900 truncate" title={entry.source_text}>
                      {entry.source_text}
                    </div>
                  </td>
                  <td className="px-4 py-3 max-w-xs">
                    {editingEntry?.id === entry.id ? (
                      <textarea
                        value={editingTargetText}
                        onChange={(e) => setEditingTargetText(e.target.value)}
                        className="w-full px-2 py-1 border border-amber-300 rounded focus:outline-none focus:ring-2 focus:ring-amber-200"
                        rows={2}
                      />
                    ) : (
                      <div className="text-amber-700 truncate" title={entry.target_text}>
                        {entry.target_text}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {LANGUAGES.find(l => l.code === entry.source_lang)?.name || entry.source_lang}
                    {' → '}
                    {LANGUAGES.find(l => l.code === entry.target_lang)?.name || entry.target_lang}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      entry.used_count > 0 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {entry.used_count} 次
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {formatDate(entry.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {editingEntry?.id === entry.id ? (
                        <>
                          <button
                            onClick={handleUpdateEntry}
                            className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
                            title="保存"
                          >
                            <Save className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setEditingEntry(null);
                              setEditingTargetText('');
                            }}
                            className="p-1.5 text-gray-600 hover:bg-gray-50 rounded transition-colors"
                            title="取消"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => copyToClipboard(entry.target_text, entry.id)}
                            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                            title="复制译文"
                          >
                            {copiedId === entry.id ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                          <button
                            onClick={() => handleEditEntry(entry)}
                            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                            title="编辑译文"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteEntry(entry.id)}
                            className="p-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            title="删除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {total > pageSize && !searchQuery && (
        <div className="p-4 bg-gray-50 border-t flex items-center justify-between">
          <div className="text-sm text-gray-600">
            显示 {(currentPage - 1) * pageSize + 1} - {Math.min(currentPage * pageSize, total)} 条，共 {total} 条
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm font-medium text-gray-700">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {notification && (
        <div className={`fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 flex items-center gap-2 ${
          notification.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`}>
          {notification.message}
          <button onClick={() => setNotification(null)} className="ml-2">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
