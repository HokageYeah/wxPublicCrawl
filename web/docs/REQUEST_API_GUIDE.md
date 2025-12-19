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

## 基本使用

### GET 请求

```typescript
import request from '@/utils/request';

// 搜索公众号
const result = await request.get('/api/v1/wx/public/search-wx-public', {
  params: { query: '关键词', begin: 0, count: 5 }
});
console.log(result); // 直接得到 data 字段内容
```

### POST 请求

```typescript
// 获取文章列表
const articleList = await request.post('/api/v1/wx/public/get-wx-article-list', {
  fakeid: 'xxx',
  begin: 0,
  count: 10
});
```

## 获取二进制数据

### 获取图片

```typescript
import request from '@/utils/request';

// 方式 1: 使用 getBlob（推荐）
async function getQRCode() {
  const blob = await request.getBlob('/api/v1/wx/public/login/get-wx-login-qrcode');
  const imageUrl = URL.createObjectURL(blob);
  return imageUrl;
}

// 方式 2: 使用普通 get 方法（需手动指定 responseType）
async function getQRCode2() {
  const blob = await request.get('/api/v1/wx/public/login/get-wx-login-qrcode', {
    responseType: 'blob'
  });
  const imageUrl = URL.createObjectURL(blob);
  return imageUrl;
}
```

### 在 Vue 组件中显示图片

```vue
<template>
  <div>
    <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="二维码" />
    <button @click="loadQRCode">加载二维码</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue';
import request from '@/utils/request';

const qrCodeUrl = ref('');

async function loadQRCode() {
  const blob = await request.getBlob('/api/v1/wx/public/login/get-wx-login-qrcode');
  qrCodeUrl.value = URL.createObjectURL(blob);
}

// 清理 URL 对象（重要！）
onUnmounted(() => {
  if (qrCodeUrl.value) {
    URL.revokeObjectURL(qrCodeUrl.value);
  }
});
</script>
```

### 下载文件

```typescript
// 方式 1: 使用 downloadFile（自动处理）
await request.downloadFile('/api/v1/files/download/123', 'document.pdf');

// 方式 2: 手动处理
const blob = await request.getBlob('/api/v1/files/download/123');
const url = URL.createObjectURL(blob);
const link = document.createElement('a');
link.href = url;
link.download = 'document.pdf';
document.body.appendChild(link);
link.click();
document.body.removeChild(link);
URL.revokeObjectURL(url);
```

## 错误处理

### 基本错误处理

```typescript
import request, { ApiError } from '@/utils/request';

try {
  const data = await request.get('/api/v1/wx/public/search-wx-public', {
    params: { query: 'test' }
  });
  console.log('成功:', data);
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API 错误:', {
      message: error.message,      // 错误消息
      code: error.code,             // 错误码
      api: error.api,               // 出错的 API
      platform: error.platform      // 平台标识
    });
  } else {
    console.error('未知错误:', error);
  }
}
```

### 根据错误码处理

```typescript
import { ApiError } from '@/utils/request';

try {
  const data = await request.post('/api/v1/wx/public/some-endpoint', params);
  // 处理成功
} catch (error) {
  if (error instanceof ApiError) {
    switch (error.code) {
      case 'UNAUTHORIZED':
        console.log('未授权，请登录');
        // 跳转到登录页
        break;
      case 'FORBIDDEN':
        console.log('没有权限');
        break;
      case 'INVALID_PARAMS':
        console.log('参数错误:', error.message);
        break;
      case 'NETWORK_ERROR':
        console.log('网络错误');
        break;
      default:
        console.log('请求失败:', error.message);
    }
  }
}
```

### 在 Vue 组件中的完整示例

```vue
<template>
  <div>
    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="data">{{ data }}</div>
    <button @click="fetchData">获取数据</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import request, { ApiError } from '@/utils/request';

const loading = ref(false);
const error = ref('');
const data = ref(null);

async function fetchData() {
  loading.value = true;
  error.value = '';
  
  try {
    data.value = await request.get('/api/v1/wx/public/search-wx-public', {
      params: { query: '关键词', begin: 0, count: 5 }
    });
  } catch (err) {
    if (err instanceof ApiError) {
      error.value = err.message;
    } else {
      error.value = '请求失败，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
}
</script>
```

## TypeScript 类型支持

### 定义返回数据类型

```typescript
// 定义返回数据的接口
interface SearchResult {
  list: Array<{
    fakeid: string;
    nickname: string;
    avatar: string;
  }>;
  total: number;
}

// 使用泛型指定返回类型
async function searchWithType(query: string) {
  const result = await request.get<SearchResult>(
    '/api/v1/wx/public/search-wx-public',
    { params: { query } }
  );
  
  // result 的类型是 SearchResult，享有完整的类型提示
  console.log(result.list[0].nickname);
  console.log(result.total);
  
  return result;
}
```

## 可用方法

### 标准 HTTP 方法

```typescript
// GET 请求
request.get<T>(url: string, config?: AxiosRequestConfig): Promise<T>

// POST 请求
request.post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>

// PUT 请求
request.put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>

// DELETE 请求
request.delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>

// PATCH 请求
request.patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>

// 通用 request 方法
request.request<T>(config: AxiosRequestConfig): Promise<T>
```

### 二进制数据方法

```typescript
// 获取 Blob 数据（图片、文件等）
request.getBlob(url: string, config?: AxiosRequestConfig): Promise<Blob>

// 获取 ArrayBuffer 数据
request.getArrayBuffer(url: string, config?: AxiosRequestConfig): Promise<ArrayBuffer>

// 下载文件
request.downloadFile(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void>
```

## 配置说明

### 基础配置

```typescript
// web/src/utils/request.ts
private baseConfig: AxiosRequestConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL,  // API 基础 URL
  timeout: 60000,                               // 超时时间 60 秒
  withCredentials: true,                        // 携带 Cookie
};
```

### 环境变量

在 `.env` 文件中配置：

```bash
# 开发环境 (.env.development)
VITE_API_BASE_URL=/web-api/api/v1/wx/public

# 生产环境 (.env.production)
VITE_API_BASE_URL=/api/v1/wx/public
```

## 注意事项

1. **类型安全**：建议为每个 API 定义具体的返回类型
2. **错误处理**：所有 API 调用都应该包装在 try-catch 中
3. **清理 URL**：使用 `URL.createObjectURL()` 后记得调用 `URL.revokeObjectURL()` 清理
4. **二进制数据**：推荐使用 `getBlob()` 方法获取图片、文件等二进制数据
5. **响应类型**：如果接口返回非 JSON 数据，确保设置正确的 `responseType`

## 常见问题

### Q: 为什么图片接口报错"响应状态字段缺失"？

A: 图片接口返回的是 Blob 数据，不是 JSON。确保使用 `getBlob()` 方法或设置 `responseType: 'blob'`。

### Q: 如何添加请求头（如 Token）？

A: 在请求拦截器中添加：

```typescript
this.instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);
```

### Q: 如何处理全局错误提示？

A: 在响应拦截器的错误处理中添加全局提示逻辑，或者创建一个 composable 统一处理。

### Q: 返回的数据类型不对怎么办？

A: 确保正确使用泛型指定返回类型：`request.get<YourType>(url)`

