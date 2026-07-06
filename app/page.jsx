'use client'

import { useState, useEffect } from 'react'

const languages = [
  { code: 'zh', name: '中文' },
  { code: 'en', name: '英语' },
  { code: 'ja', name: '日语' },
  { code: 'ko', name: '韩语' },
  { code: 'fr', name: '法语' },
  { code: 'de', name: '德语' },
  { code: 'es', name: '西班牙语' },
  { code: 'ru', name: '俄语' },
  { code: 'it', name: '意大利语' },
  { code: 'pt', name: '葡萄牙语' },
  { code: 'th', name: '泰语' },
  { code: 'vi', name: '越南语' },
  { code: 'ar', name: '阿拉伯语' },
  { code: 'hi', name: '印地语' },
]

export default function Home() {
  const [sourceText, setSourceText] = useState('')
  const [translatedText, setTranslatedText] = useState('')
  const [sourceLang, setSourceLang] = useState('zh')
  const [targetLang, setTargetLang] = useState('en')
  const [isLoading, setIsLoading] = useState(false)
  const [showSourceDropdown, setShowSourceDropdown] = useState(false)
  const [showTargetDropdown, setShowTargetDropdown] = useState(false)

  const handleSwap = () => {
    const tempLang = sourceLang
    setSourceLang(targetLang)
    setTargetLang(tempLang)
    const tempText = sourceText
    setSourceText(translatedText)
    setTranslatedText(tempText)
  }

  const handleTranslate = async () => {
    if (!sourceText.trim()) return
    
    setIsLoading(true)
    try {
      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          source: sourceLang,
          target: targetLang,
        }),
      })
      
      const data = await response.json()
      
      if (data.success) {
        setTranslatedText(data.result)
      } else {
        setTranslatedText('翻译失败：' + (data.error || '未知错误'))
      }
    } catch (error) {
      setTranslatedText('翻译失败：网络错误')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      if (sourceText.trim()) {
        handleTranslate()
      } else {
        setTranslatedText('')
      }
    }, 500)
    
    return () => clearTimeout(timer)
  }, [sourceText, sourceLang, targetLang])

  const getLangName = (code) => {
    const lang = languages.find(l => l.code === code)
    return lang ? lang.name : code
  }

  const charCount = sourceText.length

  return (
    <main className="min-h-screen bg-deepl-bg">
      <header className="bg-white border-b border-deepl-border">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-deepl-blue rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">译</span>
            </div>
            <span className="text-xl font-bold text-deepl-text">AI翻译</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-deepl-textSecondary">
            <a href="#" className="hover:text-deepl-blue transition-colors">翻译</a>
            <a href="#" className="hover:text-deepl-blue transition-colors">文档翻译</a>
            <a href="#" className="hover:text-deepl-blue transition-colors">帮助</a>
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-deepl-text mb-3">
            AI 驱动的在线翻译
          </h1>
          <p className="text-deepl-textSecondary text-lg">
            精准、快速、免费，支持多种语言互译
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-deepl-border overflow-hidden">
          <div className="flex items-center border-b border-deepl-border">
            <div className="flex-1 relative">
              <button
                onClick={() => {
                  setShowSourceDropdown(!showSourceDropdown)
                  setShowTargetDropdown(false)
                }}
                className="w-full px-6 py-3 text-left font-medium text-deepl-text hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                {getLangName(sourceLang)}
                <svg className="w-4 h-4 text-deepl-textSecondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {showSourceDropdown && (
                <div className="absolute top-full left-0 w-full bg-white border border-deepl-border rounded-b-lg shadow-lg z-10 max-h-64 overflow-y-auto scrollbar-thin">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setSourceLang(lang.code)
                        setShowSourceDropdown(false)
                      }}
                      className={`w-full px-6 py-2 text-left hover:bg-gray-50 transition-colors ${
                        lang.code === sourceLang ? 'text-deepl-blue font-medium bg-blue-50' : 'text-deepl-text'
                      }`}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="px-2">
              <button
                onClick={handleSwap}
                className="p-2 rounded-full hover:bg-gray-100 transition-colors text-deepl-textSecondary hover:text-deepl-blue"
                title="交换语言"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </button>
            </div>

            <div className="flex-1 relative">
              <button
                onClick={() => {
                  setShowTargetDropdown(!showTargetDropdown)
                  setShowSourceDropdown(false)
                }}
                className="w-full px-6 py-3 text-left font-medium text-deepl-text hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                {getLangName(targetLang)}
                <svg className="w-4 h-4 text-deepl-textSecondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {showTargetDropdown && (
                <div className="absolute top-full left-0 w-full bg-white border border-deepl-border rounded-b-lg shadow-lg z-10 max-h-64 overflow-y-auto scrollbar-thin">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setTargetLang(lang.code)
                        setShowTargetDropdown(false)
                      }}
                      className={`w-full px-6 py-2 text-left hover:bg-gray-50 transition-colors ${
                        lang.code === targetLang ? 'text-deepl-blue font-medium bg-blue-50' : 'text-deepl-text'
                      }`}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2">
            <div className="border-r border-deepl-border">
              <textarea
                value={sourceText}
                onChange={(e) => setSourceText(e.target.value)}
                placeholder="请输入要翻译的文字..."
                className="w-full h-64 p-6 text-lg outline-none bg-transparent scrollbar-thin"
              />
              <div className="px-6 py-3 border-t border-deepl-border flex items-center justify-between text-sm text-deepl-textSecondary">
                <span>{charCount} / 5000 字符</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSourceText('')}
                    className="p-1 hover:text-deepl-blue transition-colors"
                    title="清除"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-gray-50">
              <div className="h-64 p-6 text-lg overflow-y-auto scrollbar-thin">
                {isLoading ? (
                  <div className="flex items-center gap-2 text-deepl-textSecondary">
                    <div className="w-5 h-5 border-2 border-deepl-blue border-t-transparent rounded-full animate-spin"></div>
                    正在翻译...
                  </div>
                ) : translatedText ? (
                  <p className="text-deepl-text whitespace-pre-wrap">{translatedText}</p>
                ) : (
                  <p className="text-deepl-textSecondary">翻译结果将显示在这里</p>
                )}
              </div>
              <div className="px-6 py-3 border-t border-deepl-border flex items-center justify-end">
                {translatedText && !isLoading && (
                  <button
                    onClick={() => navigator.clipboard.writeText(translatedText)}
                    className="flex items-center gap-1 text-sm text-deepl-textSecondary hover:text-deepl-blue transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    复制
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-deepl-border">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-deepl-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-deepl-text mb-2">快速翻译</h3>
            <p className="text-deepl-textSecondary text-sm">实时翻译，输入即可获得结果，高效便捷</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-deepl-border">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-deepl-text mb-2">精准可靠</h3>
            <p className="text-deepl-textSecondary text-sm">基于腾讯云AI，提供高质量的翻译结果</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-deepl-border">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-deepl-text mb-2">多语言支持</h3>
            <p className="text-deepl-textSecondary text-sm">支持14种主流语言，满足各种翻译需求</p>
          </div>
        </div>
      </div>

      <footer className="border-t border-deepl-border bg-white mt-16">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-deepl-textSecondary">
          <p>© 2024 AI翻译. 基于腾讯云翻译技术驱动</p>
        </div>
      </footer>
    </main>
  )
}
