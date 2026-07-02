## 1. 架构设计

```mermaid
graph TB
    "前端 React" --> "Flask 后端API"
    "Flask 后端API" --> "OCR服务"
    "Flask 后端API" --> "翻译API"
    "OCR服务" --> "图片/PDF文件处理"
    "翻译API" --> "外部翻译服务"
```

## 2. 技术说明
- **前端**：React@18 + TailwindCSS@3 + Vite
- **初始化工具**：create-vite
- **后端**：Flask@3.0 + Flask-CORS
- **OCR处理**：pytesseract (图片) + pdf2image (PDF)
- **翻译服务**：模拟翻译API (可替换为真实API如Google Translate、百度翻译等)
- **文件存储**：本地临时存储，处理完成后删除

## 3. 路由定义

### 前端路由
| 路由 | 用途 |
|------|------|
| / | 主页面，包含文件上传、翻译操作和结果展示 |

### 后端路由
| 路由 | 方法 | 用途 |
|------|------|------|
| /api/upload | POST | 上传文件并返回文件路径 |
| /api/ocr | POST | 对上传的文件进行OCR识别 |
| /api/translate | POST | 调用翻译API进行文本翻译 |

## 4. API定义

### 4.1 上传文件API
```typescript
// POST /api/upload
interface UploadRequest {
  file: File; // 图片或PDF文件
}

interface UploadResponse {
  success: boolean;
  fileId: string;      // 文件唯一标识
  fileName: string;    // 文件名
  filePath: string;    // 服务器文件路径
  fileType: string;    // 文件类型 (image/pdf)
  message: string;
}
```

### 4.2 OCR识别API
```typescript
// POST /api/ocr
interface OCRRequest {
  fileId: string;      // 文件ID
  filePath: string;    // 文件路径
}

interface OCRResponse {
  success: boolean;
  text: string;        // 识别出的文本
  confidence: number;  // 置信度 (0-1)
  message: string;
}
```

### 4.3 翻译API
```typescript
// POST /api/translate
interface TranslateRequest {
  text: string;       // 待翻译文本
  sourceLang: string;  // 源语言代码 (如 'en', 'zh')
  targetLang: string;  // 目标语言代码
}

interface TranslateResponse {
  success: boolean;
  originalText: string;  // 原文
  translatedText: string; // 译文
  sourceLang: string;     // 源语言
  targetLang: string;     // 目标语言
  message: string;
}
```

## 5. 服务器架构图

```mermaid
graph LR
    "前端组件" --> "API路由控制器"
    "API路由控制器" --> "OCR服务层"
    "API路由控制器" --> "翻译服务层"
    "OCR服务层" --> "文件处理工具"
    "翻译服务层" --> "外部翻译API"
    "文件处理工具" --> "临时文件存储"
```

## 6. 数据模型

### 6.1 数据模型定义
本系统为无状态设计，不使用数据库。所有数据通过文件系统和API请求传递。

临时数据存储：
- 上传文件存储在 `/tmp/uploads/` 目录
- 处理完成后立即删除临时文件

### 6.2 文件命名规则
- 上传文件：`{timestamp}_{random_id}_{original_filename}`
- 最大文件大小：10MB
- 支持格式：JPG, JPEG, PNG, PDF

## 7. 项目目录结构

### 前端目录结构
```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUpload.jsx      # 文件上传组件
│   │   ├── TranslationPanel.jsx # 翻译面板组件
│   │   └── ResultDisplay.jsx   # 结果展示组件
│   ├── App.jsx                 # 主应用组件
│   ├── main.jsx                # 入口文件
│   └── index.css               # 全局样式
├── public/
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

### 后端目录结构
```
backend/
├── app.py              # Flask主应用
├── ocr_service.py      # OCR处理模块
├── translate_service.py # 翻译服务模块
├── config.py           # 配置文件
└── requirements.txt    # Python依赖
```

## 8. 外部依赖

### 前端依赖
- react: ^18.0.0
- react-dom: ^18.0.0
- tailwindcss: ^3.0.0
- axios: ^1.0.0
- react-dropzone: ^14.0.0

### 后端依赖
- Flask: ^3.0.0
- Flask-CORS: ^4.0.0
- pytesseract: ^0.3.10
- pdf2image: ^1.16.0
- Pillow: ^10.0.0