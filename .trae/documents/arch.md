## 1. Architecture Design
纯前端单页应用，使用 React + Vite + TailwindCSS 构建，无后端依赖。

```mermaid
graph TB
  A[用户访问] --> B[React 应用]
  B --> C[幻灯片组件]
  C --> D[导航控制]
  C --> E[内容展示]
```

## 2. Technology Description
- Frontend: React@18 + TypeScript + tailwindcss@3 + vite
- Initialization Tool: vite-init
- Backend: None
- Database: None

## 3. Route Definitions
| Route | Purpose |
|-------|---------|
| / | 主展示页面 |

## 4. API Definitions
无需后端API

## 5. Server Architecture Diagram
无需后端

## 6. Data Model
不适用
