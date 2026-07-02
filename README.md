# 文档翻译系统

一个基于React+Flask的文档翻译系统，支持上传图片或PDF文件，进行OCR识别和翻译。

## 系统架构

- **前端**: React 18 + TypeScript + TailwindCSS + Vite
- **后端**: Flask + Flask-CORS
- **OCR处理**: pytesseract + pdf2image
- **翻译服务**: 模拟翻译API (可替换为真实API)

## 目录结构

```
/workspace
├── frontend/          # React前端项目
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── FileUpload.tsx
│   │   │   ├── TranslationPanel.tsx
│   │   │   └── ResultDisplay.tsx
│   │   ├── pages/         # 页面
│   │   │   └── Home.tsx
│   │   ├── services/      # API服务
│   │   │   └── api.ts
│   │   └── App.tsx
│   └── package.json
├── backend/           # Flask后端项目
│   ├── app.py            # Flask主应用
│   ├── ocr_service.py    # OCR处理模块
│   ├── translate_service.py  # 翻译服务模块
│   ├── config.py         # 配置文件
│   └── requirements.txt  # Python依赖
└── .trae/
    └── documents/     # 项目文档
        ├── prd.md        # 产品需求文档
        └── technical-architecture.md  # 技术架构文档
```

## 快速开始

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

注意: 还需要安装系统依赖:
- Tesseract OCR: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- Poppler (PDF处理): `sudo apt-get install poppler-utils`

#### 前端依赖
```bash
cd frontend
npm install
```

### 启动服务

#### 启动后端服务
```bash
cd backend
python app.py
```
后端将在 http://localhost:5000 运行

#### 启动前端服务
```bash
cd frontend
npm run dev
```
前端将在 http://localhost:5173 运行

## 功能说明

1. **文件上传**: 支持拖拽或点击上传图片(JPG/PNG)和PDF文件，最大10MB
2. **OCR识别**: 自动识别上传文件中的文本内容
3. **翻译功能**: 支持多语言翻译(英文、中文、日文、韩文等)
4. **结果展示**: 左右对照显示原文和译文，支持复制和下载

## API接口

### 上传文件
- **POST** `/api/upload`
- 参数: `file` (FormData)
- 返回: 文件ID、路径、类型等信息

### OCR识别
- **POST** `/api/ocr`
- 参数: `filePath`
- 返回: 识别文本、置信度

### 翻译
- **POST** `/api/translate`
- 参数: `text`, `sourceLang`, `targetLang`
- 返回: 原文、译文

## 注意事项

1. 翻译服务目前使用模拟API，实际部署时需要替换为真实翻译API
2. OCR需要安装Tesseract和对应语言包
3. PDF处理需要安装Poppler工具
4. 上传文件保存在临时目录，处理完成后自动删除

## 技术特点

- 响应式设计，支持桌面和移动端
- TypeScript类型安全
- TailwindCSS样式系统
- React组件化开发
- Flask RESTful API
- 文件处理和OCR集成
- 可扩展的翻译服务架构