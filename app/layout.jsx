import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AI翻译 - 精准、快速的在线翻译',
  description: '基于腾讯云翻译的高质量在线翻译工具，支持多种语言互译',
}

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
