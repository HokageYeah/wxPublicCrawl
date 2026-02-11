# Request API 使用指南

## 概述

`request.ts` 是项目的 HTTP 请求封装类，基于 axios，提供了完整的类型支持和错误处理。

## 主要特性

### 1. 自动处理服务器响应格式

服务器返回格式：
```json
{
  "platform": "WX_PUBLIC",
  "api": "api/v1/wx/public/search-wx-public",
  "ret": ["SUCCESS::请求成功"],
  "v": 1,
  "data": { /* 实际数据 */ }
}
```

Request 类自动处理：
- ✅ 成功时：直接返回 `data` 字段
- ❌ 失败时：抛出 `ApiError`，包含详细错误信息

### 2. 智能识别二进制数据

自动检测并直接返回二进制数据（Blob、ArrayBuffer、图片等），不进行 JSON 解析。

### 3. 完善的错误处理

- API 业务错误（ret 不为 SUCCESS）
- HTTP 状态码错误（4xx、5xx）
- 网络错误
- 请求配置错误

---

## 🌐 环境配置与请求流程

### 架构概览

项目支持两种运行环境：

1. **开发环境**：Vite 开发服务器 + FastAPI 后端
2. **桌面应用环境**：打包后的桌面应用，前端静态文件 + FastAPI 后端

### 开发环境架构

```
┌─────────────────────┐
│  Vite Dev Server   │  端口: 5173
│   (前端开发服务器)  │
└─────────┬───────────┘
          │ 代理
          ↓
┌─────────────────────┐
│   FastAPI Backend   │  端口: 8002
│   (后端 API 服务器)  │
└─────────────────────┘
```

**配置文件**:
- `web/vite.config.ts` - Vite 开发服务器配置
- `web/.env.development` - 开发环境变量

**请求流程**:
1. 前端代码运行在 `http://localhost:5173`
2. API 请求 baseURL: `/web-api/api/v1/wx/public`
3. Vite 代理将 `/web-api/*` 转发到 `http://127.0.0.1:8002`
4. FastAPI 接收请求并返回数据

### 桌面应用环境架构

```
┌─────────────────────────────────────┐
│       WebView Window               │  端口: 18000
│  ┌─────────────────────────────┐   │
│  │  静态前端文件 (web/dist)   │   │
│  │  - HTML/CSS/JS             │   │
│  └─────────────────────────────┘   │
│                                    │
│  ┌─────────────────────────────┐   │
│  │   FastAPI Backend          │   │
│  │   - API 路由               │   │
│  │   - 静态文件服务           │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**配置文件**:
- `run_desktop.py` - 桌面应用启动脚本
- `web/.env.production` - 生产环境变量
- `app/main.py` - FastAPI 主应用配置

**请求流程**:
1. WebView 加载 `http://127.0.0.1:18000/crawl-desktop/`
2. 前端静态文件由 FastAPI 的 `StaticFiles` 提供
3. API 请求 baseURL: `/api/v1/wx/public`（相对路径）
4. 同域请求，无需代理，直接由 FastAPI 处理

---

## 🔧 详细配置说明

### 1. Vite 开发服务器配置

**文件**: `web/vite.config.ts`

```typescript
export default defineConfig({
  base: '/crawl-desktop/',  // 项目部署路径

  // 开发服务器配置
  server: {
    proxy: {
      '/web-api': {
        target: 'http://127.0.0.1:8002',  // 后端服务器地址
        changeOrigin: true,                // 改变请求头的 origin
        rewrite: (path) => path.replace(/^\/web-api/, '')  // 重写路径
      }
    }
  }
});
```

**工作原理**:
```
前端请求: /web-api/api/v1/wx/public/search-wx-public
    ↓ (Vite 代理重写)
实际请求: http://127.0.0.1:8002/api/v1/wx/public/search-wx-public
```

### 2. 环境变量配置

**开发环境** - `web/.env.development`:
```bash
VITE_API_BASE_URL=/web-api/api/v1/wx/public
```

**生产环境** - `web/.env.production`:
```bash
VITE_API_BASE_URL=/api/v1/wx/public
```

### 3. 桌面应用启动配置

**文件**: `run_desktop.py`

```python
# 固定端口配置
PORT = 18000

# FastAPI 服务器配置
config = uvicorn.Config(
    app=app,
    host="127.0.0.1",
    port=PORT,  # 18000
    log_level="info"
)

# WebView 窗口配置
window = webview.create_window(
    '公众号爬虫助手',
    f'http://127.0.0.1:{PORT}/crawl-desktop/',  # http://127.0.0.1:18000/crawl-desktop/
    width=1280,
    height=1000,
    resizable=True
)
```

### 4. FastAPI 静态文件服务

**文件**: `app/main.py`

```python
# 获取前端资源路径
web_dist_path = get_resource_path("web/dist")

if os.path.exists(web_dist_path):
    from fastapi.staticfiles import StaticFiles

    # 挂载静态资源
    app.mount("/crawl-desktop/assets", StaticFiles(directory=assets_path), name="assets")

    # 根路径跳转
    @app.get("/")
    async def root():
        return RedirectResponse("/crawl-desktop/")

    # SPA 路由处理（支持前端路由）
    @app.get("/crawl-desktop", include_in_schema=False)
    @app.get("/crawl-desktop/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # 尝试直接服务文件
        if full_path:
            file_path = os.path.join(web_dist_path, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)

        # 返回 index.html（Vue Router 处理）
        index_path = os.path.join(web_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
```

---

## 📊 端口配置对比表

| 配置项 | 开发环境 | 桌面环境 | 说明 |
|--------|---------|---------|------|
| **前端服务器** | Vite 5173 | 无（静态文件） | 桌面环境由 FastAPI 提供静态文件 |
| **后端服务器** | FastAPI 8002 | FastAPI 18000 | 桌面环境后端使用 18000 端口 |
| **前端 URL** | http://localhost:5173 | http://127.0.0.1:18000/crawl-desktop/ | 桌面环境是同一个服务 |
| **API baseURL** | `/web-api/api/v1/wx/public` | `/api/v1/wx/public` | 开发环境需要代理前缀 |
| **代理配置** | 需要配置 Vite 代理 | 不需要代理 | 桌面环境同域请求 |
| **后端实际端口** | 8002 | 18000 | 后端服务器的监听端口 |

---

## 🔑 核心要点

### 为什么桌面环境不需要端口转换？

**同域请求原理**:
```
前端页面: http://127.0.0.1:18000/crawl-desktop/
API 请求: http://127.0.0.1:18000/api/v1/wx/public/xxx
```

- ✅ **同一个域名**: `127.0.0.1`
- ✅ **同一个端口**: `18000`
- ✅ **只是路径不同**: `/crawl-desktop/` vs `/api/v1/`
- ✅ **无需代理**: 同域请求直接发送

**代码层面**:
```typescript
// 前端代码使用相对路径（不包含端口）
baseURL: '/api/v1/wx/public'

// 浏览器自动拼接为当前域名和端口
// 开发环境: http://localhost:5173/api/v1/... (通过代理)
// 桌面环境: http://127.0.0.1:18000/api/v1/... (同域直接请求)
```

### 端口转换问题

**问题**: MCP Server 硬编码了 `localhost:8002`，在桌面环境无法连接

**原因**:
```python
# 错误的写法
session_url = "http://localhost:8002/api/v1/wx/public/system/session/load"
```

**解决方案**:
```python
import os

def get_backend_url():
    """根据环境获取后端服务器URL"""
    env = os.environ.get('ENV', '')
    if env == 'desktop':
        return "http://127.0.0.1:18000"
    else:
        return "http://localhost:8002"

# 使用动态 URL
backend_url = get_backend_url()
session_url = f"{backend_url}/api/v1/wx/public/system/session/load"
```

---

## 📝 请求 URL 拼接示例

### 开发环境

```javascript
// 1. 环境变量
VITE_API_BASE_URL = '/web-api/api/v1/wx/public'

// 2. Request 配置
baseURL = import.meta.env.VITE_API_BASE_URL  // '/web-api/api/v1/wx/public'

// 3. 前端请求
request.get('/search-wx-public', { params: { query: 'test' } })

// 4. 完整 URL 拼接
// 浏览器端: http://localhost:5173/web-api/api/v1/wx/public/search-wx-public
//         ↓ Vite 代理转发
// 实际请求: http://127.0.0.1:8002/api/v1/wx/public/search-wx-public
```

### 桌面应用环境

```javascript
// 1. 环境变量（生产构建时设置）
VITE_API_BASE_URL = '/api/v1/wx/public'

// 2. Request 配置
baseURL = import.meta.env.VITE_API_BASE_URL  // '/api/v1/wx/public'

// 3. 前端请求
request.get('/search-wx-public', { params: { query: 'test' } })

// 4. 完整 URL 拼接
// 浏览器端: http://127.0.0.1:18000/api/v1/wx/public/search-wx-public
//         ↓ 同域请求，无需代理
// FastAPI 直接处理（同一服务）
```

### 对比图

```
开发环境请求链:
浏览器 → http://localhost:5173/web-api/... → Vite代理 → http://127.0.0.1:8002/api/v1/... → FastAPI

桌面应用请求链:
浏览器 → http://127.0.0.1:18000/api/v1/... → FastAPI (同一服务)
```

---

## 🚀 前端构建与部署

### 开发环境运行

```bash
# 1. 安装依赖
cd web && npm install

# 2. 启动开发服务器
npm run dev
# 前端: http://localhost:5173
# 后端: 需要单独启动 python run_app.py (端口 8002)
```

### 桌面应用打包

```bash
# 1. 构建前端（生产环境）
cd web
npm run build:only  # 生成 web/dist 目录

# 2. 打包桌面应用
cd ..
python -m pyinstaller wx_crawler.spec

# 3. 运行桌面应用
# macOS: open dist/wx公众号工具.app
# Windows: dist\wx公众号工具\wx公众号工具.exe
```

### 构建命令说明

**npm run build** (完整构建):
```bash
# 1. TypeScript 类型检查
vue-tsc --noEmit

# 2. Vite 构建前端
vite build
```

**npm run build:only** (仅构建，跳过类型检查):
```bash
# 仅执行 Vite 构建，更快
vite build
```

---

## 💡 最佳实践

### 1. 使用相对路径

✅ **推荐**:
```typescript
// 使用环境变量，相对路径
const baseURL = import.meta.env.VITE_API_BASE_URL;
```

❌ **不推荐**:
```typescript
// 硬编码绝对路径
const baseURL = 'http://localhost:8002/api/v1/wx/public';
```

### 2. 环境判断

```typescript
// 判断当前环境
if (import.meta.env.DEV) {
  console.log('开发环境');
} else if (import.meta.env.PROD) {
  console.log('生产环境');
}
```

### 3. 错误处理

所有 API 调用都应该包装在 try-catch 中：
```typescript
import request, { ApiError } from '@/utils/request';

try {
  const data = await request.get('/api/v1/wx/public/search-wx-public', {
    params: { query: 'test' }
  });
  console.log('成功:', data);
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API 错误:', error.message);
    // 处理特定错误码
    switch (error.code) {
      case 'UNAUTHORIZED':
        // 跳转登录页
        break;
      case 'NETWORK_ERROR':
        // 显示网络错误提示
        break;
    }
  }
}
```

### 4. 类型安全

为 API 返回数据定义类型：
```typescript
interface SearchResult {
  list: Array<{
    fakeid: string;
    nickname: string;
    avatar: string;
  }>;
  total: number;
}

// 使用泛型
const result = await request.get<SearchResult>('/api/v1/wx/public/search-wx-public', {
  params: { query: 'test' }
});

// 类型提示完整
console.log(result.list[0].nickname);  // ✅ 类型安全
```

---

## 🐛 常见问题

### Q: 为什么桌面环境 API 请求失败？

**A**: 检查以下几点：
1. 环境变量 `VITE_API_BASE_URL` 是否正确设置为 `/api/v1/wx/public`
2. 是否重新构建前端（`npm run build:only`）
3. FastAPI 服务器是否正常运行在 18000 端口
4. 浏览器控制台是否有跨域错误

### Q: 开发环境代理不生效？

**A**: 检查：
1. `vite.config.ts` 中的 proxy 配置是否正确
2. 后端服务器是否运行在 8002 端口
3. 重启 Vite 开发服务器

### Q: 打包后前端空白页面？

**A**: 检查：
1. `web/dist` 目录是否存在且不为空
2. `wx_crawler.spec` 中是否包含 `('web/dist', 'web/dist')`
3. 重新构建前端：`cd web && npm run build:only && cd ..`

### Q: 如何调试请求 URL？

**A**: 使用浏览器开发者工具：
1. 打开 Network 面板
2. 发送 API 请求
3. 查看请求的完整 URL 和响应

### Q: MCP Server 连接失败？

**A**: 这是之前遇到的问题，已解决：
1. 确保使用动态 URL：`get_backend_url()`
2. 检查环境变量 `ENV=desktop` 是否设置
3. 桌面环境后端应该运行在 18000 端口

---

## 📚 相关文件清单

| 文件路径 | 说明 |
|---------|------|
| `web/src/utils/request.ts` | HTTP 请求封装 |
| `web/vite.config.ts` | Vite 开发服务器配置 |
| `web/.env.development` | 开发环境变量 |
| `web/.env.production` | 生产环境变量 |
| `web/vite-env.d.ts` | 环境变量类型定义 |
| `run_desktop.py` | 桌面应用启动脚本 |
| `app/main.py` | FastAPI 主应用配置 |
| `app/ai/mcp/mcp_server/fastmcp_server.py` | MCP 服务器配置 |
| `wx_crawler.spec` | PyInstaller 打包配置 |

---

## 📖 参考链接

- [Vite 代理配置](https://vitejs.dev/config/server-options.html#server-proxy)
- [Axios 文档](https://axios-http.com/)
- [FastAPI 静态文件](https://fastapi.tiangolo.com/tutorial/static-files/)
- [PyWebView 文档](https://pywebview.flowrl.com/)

---

*最后更新: 2026-01-08*
