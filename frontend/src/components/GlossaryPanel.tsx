import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Edit2, Trash2, Search, Download, Upload, X, Save, ChevronDown } from 'lucide-react';
import { getGlossary, addGlossaryTerm, updateGlossaryTerm, deleteGlossaryTerm, exportGlossary, importGlossary, GlossaryTerm } from '@/services/api';

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

export default function GlossaryPanel() {
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceLangFilter, setSourceLangFilter] = useState('');
  const [targetLangFilter, setTargetLangFilter] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTerm, setEditingTerm] = useState<GlossaryTerm | null>(null);
  const [formData, setFormData] = useState({
    sourceTerm: '',
    targetTerm: '',
    sourceLang: 'en',
    targetLang: 'zh',
    description: '',
    caseSensitive: false,
    priority: 0,
  });
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const loadTerms = async () => {
    setLoading(true);
    try {
      const response = await getGlossary(sourceLangFilter || undefined, targetLangFilter || undefined);
      setTerms(response.glossary);
    } catch (error) {
      setNotification({ type: 'error', message: '加载术语表失败' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTerms();
  }, [sourceLangFilter, targetLangFilter]);

  const handleAddTerm = async () => {
    if (!formData.sourceTerm || !formData.targetTerm) {
      setNotification({ type: 'error', message: '请填写源术语和目标术语' });
      return;
    }

    try {
      await addGlossaryTerm(formData);
      setNotification({ type: 'success', message: '添加术语成功' });
      setShowAddModal(false);
      setFormData({
        sourceTerm: '',
        targetTerm: '',
        sourceLang: 'en',
        targetLang: 'zh',
        description: '',
        caseSensitive: false,
        priority: 0,
      });
      loadTerms();
    } catch (error) {
      setNotification({ type: 'error', message: '添加术语失败' });
    }
  };

  const handleEditTerm = (term: GlossaryTerm) => {
    setEditingTerm(term);
    setFormData({
      sourceTerm: term.source_term,
      targetTerm: term.target_term,
      sourceLang: term.source_lang,
      targetLang: term.target_lang,
      description: term.description,
      caseSensitive: term.case_sensitive,
      priority: term.priority,
    });
  };

  const handleUpdateTerm = async () => {
    if (!editingTerm || !formData.sourceTerm || !formData.targetTerm) {
      setNotification({ type: 'error', message: '请填写完整信息' });
      return;
    }

    try {
      await updateGlossaryTerm(editingTerm.id, {
        sourceTerm: formData.sourceTerm,
        targetTerm: formData.targetTerm,
        sourceLang: formData.sourceLang,
        targetLang: formData.targetLang,
        description: formData.description,
        caseSensitive: formData.caseSensitive,
        priority: formData.priority,
      });
      setNotification({ type: 'success', message: '更新术语成功' });
      setEditingTerm(null);
      setFormData({
        sourceTerm: '',
        targetTerm: '',
        sourceLang: 'en',
        targetLang: 'zh',
        description: '',
        caseSensitive: false,
        priority: 0,
      });
      loadTerms();
    } catch (error) {
      setNotification({ type: 'error', message: '更新术语失败' });
    }
  };

  const handleDeleteTerm = async (termId: string) => {
    if (!confirm('确定要删除这个术语吗？')) return;

    try {
      await deleteGlossaryTerm(termId);
      setNotification({ type: 'success', message: '删除术语成功' });
      loadTerms();
    } catch (error) {
      setNotification({ type: 'error', message: '删除术语失败' });
    }
  };

  const handleExport = async () => {
    try {
      const response = await exportGlossary(sourceLangFilter || undefined, targetLangFilter || undefined);
      const dataStr = JSON.stringify(response.glossary, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'glossary.json';
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
      const termsData = JSON.parse(text);
      await importGlossary(termsData);
      setNotification({ type: 'success', message: '导入成功' });
      loadTerms();
    } catch (error) {
      setNotification({ type: 'error', message: '导入失败，请确保文件格式正确' });
    }
  };

  const filteredTerms = terms.filter(term => {
    const matchesSearch = term.source_term.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         term.target_term.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-purple-600" />
            <h2 className="text-lg font-semibold text-gray-800">术语库管理</h2>
            <span className="text-xs px-2 py-0.5 bg-purple-200 text-purple-700 rounded-full">
              {terms.length} 条
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
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all shadow-md"
            >
              <Plus className="w-4 h-4" />
              <span className="font-medium">添加术语</span>
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
              placeholder="搜索术语..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400"
            />
          </div>
          <div className="flex gap-3">
            <select
              value={sourceLangFilter}
              onChange={(e) => setSourceLangFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400 bg-white"
            >
              <option value="">全部源语言</option>
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
            <select
              value={targetLangFilter}
              onChange={(e) => setTargetLangFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400 bg-white"
            >
              <option value="">全部目标语言</option>
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">源术语</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">目标术语</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">语言</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">描述</th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">优先级</th>
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
            ) : filteredTerms.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  暂无术语，点击右上角添加
                </td>
              </tr>
            ) : (
              filteredTerms.map((term) => (
                <tr key={term.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{term.source_term}</div>
                    {term.case_sensitive && (
                      <div className="text-xs text-gray-400">区分大小写</div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-purple-700">{term.target_term}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {LANGUAGES.find(l => l.code === term.source_lang)?.name || term.source_lang}
                    {' → '}
                    {LANGUAGES.find(l => l.code === term.target_lang)?.name || term.target_lang}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" title={term.description}>
                    {term.description || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      term.priority > 0 ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {term.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEditTerm(term)}
                        className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="编辑"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteTerm(term.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="删除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {(showAddModal || editingTerm) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-800">
                {editingTerm ? '编辑术语' : '添加术语'}
              </h3>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingTerm(null);
                  setFormData({
                    sourceTerm: '',
                    targetTerm: '',
                    sourceLang: 'en',
                    targetLang: 'zh',
                    description: '',
                    caseSensitive: false,
                    priority: 0,
                  });
                }}
                className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">源语言</label>
                  <select
                    value={formData.sourceLang}
                    onChange={(e) => setFormData({ ...formData, sourceLang: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400"
                  >
                    {LANGUAGES.map((lang) => (
                      <option key={lang.code} value={lang.code}>{lang.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">目标语言</label>
                  <select
                    value={formData.targetLang}
                    onChange={(e) => setFormData({ ...formData, targetLang: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400"
                  >
                    {LANGUAGES.map((lang) => (
                      <option key={lang.code} value={lang.code}>{lang.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">源术语</label>
                <input
                  type="text"
                  value={formData.sourceTerm}
                  onChange={(e) => setFormData({ ...formData, sourceTerm: e.target.value })}
                  placeholder="输入源术语"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">目标术语</label>
                <input
                  type="text"
                  value={formData.targetTerm}
                  onChange={(e) => setFormData({ ...formData, targetTerm: e.target.value })}
                  placeholder="输入目标术语（译文）"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述（可选）</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="术语的说明或上下文"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400 resize-none"
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.caseSensitive}
                    onChange={(e) => setFormData({ ...formData, caseSensitive: e.target.checked })}
                    className="w-4 h-4 text-purple-600 rounded focus:ring-purple-200"
                  />
                  <span className="text-sm text-gray-700">区分大小写</span>
                </label>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-700">优先级:</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                    className="px-2 py-1 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-purple-200"
                  >
                    <option value={0}>0 - 普通</option>
                    <option value={1}>1 - 较高</option>
                    <option value={2}>2 - 高</option>
                    <option value={3}>3 - 最高</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 p-4 border-t bg-gray-50">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingTerm(null);
                  setFormData({
                    sourceTerm: '',
                    targetTerm: '',
                    sourceLang: 'en',
                    targetLang: 'zh',
                    description: '',
                    caseSensitive: false,
                    priority: 0,
                  });
                }}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={editingTerm ? handleUpdateTerm : handleAddTerm}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all"
              >
                <Save className="w-4 h-4" />
                {editingTerm ? '保存修改' : '添加术语'}
              </button>
            </div>
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
