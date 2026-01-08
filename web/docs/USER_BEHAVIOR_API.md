# 用户行为管理 API 文档

## 概述

用户行为管理系统用于存储和管理用户在桌面程序中的个人设置和行为偏好，替代原有的 `localStorage` 方案，确保数据在桌面应用中能够持久化保存。

## 数据模型

### UserBehavior 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键ID（自增） |
| user_id | String(100) | 用户ID（uin 或 nick_name），建立索引 |
| behavior_type | String(50) | 行为类型，建立索引 |
| behavior_value | String(1000) | 行为值 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### BehaviorType 常量

```python
class BehaviorType:
    # 下载路径保存行为
    SAVE_DOWNLOAD_PATH = "SAVE_DOWNLOAD_PATH"

    # 是否保存到本地（1: 是，2: 否）
    SAVE_TO_LOCAL = "SAVE_TO_LOCAL"

    # 是否上传到阿里云（1: 是，2: 否）
    UPLOAD_TO_ALIYUN = "UPLOAD_TO_ALIYUN"

    # 搜索历史
    SEARCH_HISTORY = "SEARCH_HISTORY"
```

---

## API 接口

### 1. 通用用户行为管理

#### 1.1 获取用户行为

**接口**: `GET /api/v1/system/user-behavior`

**请求参数**:
```typescript
{
  user_id: string,  // 用户ID（uin 或 nick_name）
  behavior_type: string  // 行为类型
}
```

**响应示例**:
```json
{
  "success": true,
  "value": "/Users/xxx/Downloads"
}
```

**前端调用示例**:
```typescript
const value = await request.get<{success: boolean, value?: string}>('/system/user-behavior', {
  params: {
    user_id: '123456',
    behavior_type: 'SAVE_DOWNLOAD_PATH'
  }
});
```

#### 1.2 设置用户行为

**接口**: `POST /api/v1/system/user-behavior`

**请求体**:
```typescript
{
  user_id: string,       // 用户ID（uin 或 nick_name）
  behavior_type: string,  // 行为类型
  behavior_value: string  // 行为值
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "保存成功"
}
```

**前端调用示例**:
```typescript
await request.post('/system/user-behavior', {
  user_id: '123456',
  behavior_type: 'SAVE_DOWNLOAD_PATH',
  behavior_value: '/Users/xxx/Downloads'
});
```

#### 1.3 删除用户行为

**接口**: `DELETE /api/v1/system/user-behavior`

**请求参数**:
```typescript
{
  user_id: string,  // 用户ID（uin 或 nick_name）
  behavior_type: string  // 行为类型
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "删除成功"
}
```

**前端调用示例**:
```typescript
await request.delete('/system/user-behavior', {
  params: {
    user_id: '123456',
    behavior_type: 'SAVE_DOWNLOAD_PATH'
  }
});
```

#### 1.4 获取用户所有行为

**接口**: `GET /api/v1/system/user-behaviors`

**请求参数**:
```typescript
{
  user_id: string  // 用户ID（uin 或 nick_name）
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "SAVE_DOWNLOAD_PATH",
      "value": "/Users/xxx/Downloads",
      "created_at": "2026-01-08T10:00:00",
      "updated_at": "2026-01-08T10:00:00"
    },
    {
      "id": 2,
      "type": "SAVE_TO_LOCAL",
      "value": "1",
      "created_at": "2026-01-08T10:00:00",
      "updated_at": "2026-01-08T10:00:00"
    }
  ]
}
```

---

### 2. 便捷方法 API

#### 2.1 下载路径管理

##### 获取下载路径

**接口**: `GET /api/v1/system/download-path`

**请求参数**:
```typescript
{
  user_id: string  // 用户ID（uin 或 nick_name）
}
```

**响应示例**:
```json
{
  "success": true,
  "path": "/Users/xxx/Downloads"
}
```

**前端调用示例**:
```typescript
const res = await request.get<{success: boolean, path?: string}>('/system/download-path', {
  params: { user_id: '123456' }
});
if (res.success && res.path) {
  downloadPath.value = res.path;
}
```

##### 设置下载路径

**接口**: `POST /api/v1/system/download-path`

**请求体**:
```typescript
{
  user_id: string,        // 用户ID（uin 或 nick_name）
  download_path: string    // 下载路径
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "保存成功"
}
```

**前端调用示例**:
```typescript
await request.post('/system/download-path', {
  user_id: '123456',
  download_path: '/Users/xxx/Downloads'
});
```

#### 2.2 是否保存到本地管理

##### 获取是否保存到本地

**接口**: `GET /api/v1/system/save-to-local`

**请求参数**:
```typescript
{
  user_id: string  // 用户ID（uin 或 nick_name）
}
```

**响应示例**:
```json
{
  "success": true,
  "value": "1"
}
```

**前端调用示例**:
```typescript
const res = await request.get<{success: boolean, value?: string}>('/system/save-to-local', {
  params: { user_id: '123456' }
});
if (res.success && res.value) {
  isSaveToLocal.value = res.value === "1";
}
```

##### 设置是否保存到本地

**接口**: `POST /api/v1/system/save-to-local`

**请求体**:
```typescript
{
  user_id: string,      // 用户ID（uin 或 nick_name）
  save_to_local: string  // "1" 表示是，"2" 表示否
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "保存成功"
}
```

**前端调用示例**:
```typescript
await request.post('/system/save-to-local', {
  user_id: '123456',
  save_to_local: '1'  // "1" = 保存到本地，"2" = 不保存
});
```

#### 2.3 是否上传到阿里云管理

##### 获取是否上传到阿里云

**接口**: `GET /api/v1/system/upload-to-aliyun`

**请求参数**:
```typescript
{
  user_id: string  // 用户ID（uin 或 nick_name）
}
```

**响应示例**:
```json
{
  "success": true,
  "value": "1"
}
```

**前端调用示例**:
```typescript
const res = await request.get<{success: boolean, value?: string}>('/system/upload-to-aliyun', {
  params: { user_id: '123456' }
});
if (res.success && res.value) {
  isUploadToAliyun.value = res.value === "1";
}
```

##### 设置是否上传到阿里云

**接口**: `POST /api/v1/system/upload-to-aliyun`

**请求体**:
```typescript
{
  user_id: string,          // 用户ID（uin 或 nick_name）
  upload_to_aliyun: string  // "1" 表示是，"2" 表示否
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "保存成功"
}
```

**前端调用示例**:
```typescript
await request.post('/system/upload-to-aliyun', {
  user_id: '123456',
  upload_to_aliyun: '1'  // "1" = 上传到阿里云，"2" = 不上传
});
```

---

## 使用场景

### 场景 1: 保存和恢复下载路径

**前端代码示例** (ArticleList.vue):
```typescript
import { ref, watch, onMounted } from 'vue';
import { useWechatStore } from '@/stores/wechatLoginStore';
import request from '@/utils/request';

const wechatStore = useWechatStore();
const downloadPath = ref('');
const isSaveToLocal = ref(true);

// 1. 监听 downloadPath 变化并保存到数据库
watch(downloadPath, async (newPath) => {
  if (isSaveToLocal.value && wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId && newPath) {
      try {
        await request.post('/system/download-path', {
          user_id: userId,
          download_path: newPath
        });
        console.log('下载路径已保存到数据库:', newPath);
      } catch (error) {
        console.error('保存下载路径失败:', error);
      }
    }
  }
});

// 2. 组件挂载时从数据库恢复
onMounted(async () => {
  if (wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId) {
      try {
        const res = await request.get<{success: boolean, path?: string}>('/system/download-path', {
          params: { user_id: userId }
        });
        if (res.success && res.path) {
          downloadPath.value = res.path;
          console.log('从数据库加载下载路径:', res.path);
        }
      } catch (error) {
        console.error('加载下载路径失败:', error);
      }
    }
  }
});
```

### 场景 2: 保存和恢复"是否保存到本地"设置

**前端代码示例** (ArticleList.vue):
```typescript
// 1. 监听 isSaveToLocal 变化并保存到数据库
watch(isSaveToLocal, async (newValue) => {
  if (wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId) {
      try {
        await request.post('/system/save-to-local', {
          user_id: userId,
          save_to_local: newValue ? "1" : "2"
        });
        console.log('保存到本地设置已保存到数据库:', newValue ? "1" : "2");
      } catch (error) {
        console.error('保存保存到本地设置失败:', error);
      }
    }
  }
});

// 2. 组件挂载时从数据库恢复
onMounted(async () => {
  if (wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId) {
      try {
        const saveRes = await request.get<{success: boolean, value?: string}>('/system/save-to-local', {
          params: { user_id: userId }
        });
        if (saveRes.success && saveRes.value) {
          isSaveToLocal.value = saveRes.value === "1";
          console.log('从数据库加载保存到本地设置:', isSaveToLocal.value);
        }
      } catch (error) {
        console.error('加载保存到本地设置失败:', error);
      }
    }
  }
});
```

### 场景 3: 保存和恢复"是否上传到阿里云"设置

**前端代码示例** (ArticleList.vue):
```typescript
const isUploadToAliyun = ref(false);

// 1. 监听 isUploadToAliyun 变化并保存到数据库
watch(isUploadToAliyun, async (newValue) => {
  if (wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId) {
      try {
        await request.post('/system/upload-to-aliyun', {
          user_id: userId,
          upload_to_aliyun: newValue ? "1" : "2"
        });
        console.log('上传到阿里云设置已保存到数据库:', newValue ? "1" : "2");
      } catch (error) {
        console.error('保存上传到阿里云设置失败:', error);
      }
    }
  }
});

// 2. 组件挂载时从数据库恢复
onMounted(async () => {
  if (wechatStore.userInfo) {
    const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
    if (userId) {
      try {
        const uploadRes = await request.get<{success: boolean, value?: string}>('/system/upload-to-aliyun', {
          params: { user_id: userId }
        });
        if (uploadRes.success && uploadRes.value) {
          isUploadToAliyun.value = uploadRes.value === "1";
          console.log('从数据库加载上传到阿里云设置:', isUploadToAliyun.value);
        }
      } catch (error) {
        console.error('加载上传到阿里云设置失败:', error);
      }
    }
  }
});
```

---

## 后端实现

### SystemManager 方法

#### 通用方法

```python
# 设置用户行为
system_manager.set_user_behavior(user_id, behavior_type, behavior_value)

# 获取用户行为值
system_manager.get_user_behavior(user_id, behavior_type)

# 删除用户行为
system_manager.delete_user_behavior(user_id, behavior_type)

# 获取用户所有行为
system_manager.get_all_user_behaviors(user_id)
```

#### 便捷方法

```python
# 下载路径管理
system_manager.set_download_path(user_id, download_path)
system_manager.get_download_path(user_id)

# 是否保存到本地管理
system_manager.set_save_to_local(user_id, save_to_local)
system_manager.get_save_to_local(user_id)

# 是否上传到阿里云管理
system_manager.set_upload_to_aliyun(user_id, upload_to_aliyun)
system_manager.get_upload_to_aliyun(user_id)
```

---

## 数据库表结构

### 创建表

表结构会在应用启动时自动创建（如果使用 SQLite），参考 `app/db/sqlalchemy_db.py:59`:

```python
if is_sqlite:
    Base.metadata.create_all(self._engine)
    logging.info("SQLite 数据库表结构已创建")
```

### 手动创建表

如果需要手动创建表，可以运行:

```bash
python -c "from app.models import Base; from app.db.sqlalchemy_db import database; database.connect(); Base.metadata.create_all(database._engine)"
```

---

## 迁移说明

### 从 localStorage 迁移到数据库

**旧方式** (localStorage):
```typescript
// 保存
localStorage.setItem(`downloadPath_${userId}`, path);

// 加载
const path = localStorage.getItem(`downloadPath_${userId}`);
```

**新方式** (数据库):
```typescript
// 保存
await request.post('/system/download-path', {
  user_id: userId,
  download_path: path
});

// 加载
const res = await request.get<{success: boolean, path?: string}>('/system/download-path', {
  params: { user_id: userId }
});
const path = res.path;
```

### 数据迁移脚本（可选）

如果需要将现有 localStorage 数据迁移到数据库，可以在前端添加迁移逻辑:

```typescript
async function migrateLocalStorageToDB() {
  const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
  if (!userId) return;

  // 迁移下载路径
  const localPath = localStorage.getItem(`downloadPath_${userId}`);
  if (localPath) {
    await request.post('/system/download-path', {
      user_id: userId,
      download_path: localPath
    });
    localStorage.removeItem(`downloadPath_${userId}`);
    console.log('已迁移下载路径到数据库');
  }
}

// 在应用启动时调用
migrateLocalStorageToDB();
```

---

## 常见问题

### Q: 为什么不使用 localStorage？

**A**: 桌面应用中，每次重新打开应用，localStorage 可能会被清空或无法正确读取。使用数据库可以确保数据持久化，并且在多用户场景下可以正确区分不同用户的设置。

### Q: 如何扩展新的用户行为类型？

**A**: 在 `BehaviorType` 类中添加新的常量:
```python
class BehaviorType:
    SAVE_DOWNLOAD_PATH = "SAVE_DOWNLOAD_PATH"
    SAVE_TO_LOCAL = "SAVE_TO_LOCAL"
    # 添加新类型
    THEME_COLOR = "THEME_COLOR"
    FONT_SIZE = "FONT_SIZE"
```

然后使用通用 API:
```python
# 后端
system_manager.set_user_behavior(user_id, BehaviorType.THEME_COLOR, 'dark')

# 前端
await request.post('/system/user-behavior', {
  user_id: userId,
  behavior_type: 'THEME_COLOR',
  behavior_value: 'dark'
});
```

### Q: 如何查看数据库中的用户行为？

**A**: 使用 SQLite 客户端查看:
```bash
# macOS/Linux
sqlite3 ~/Library/Application\ Support/wx公众号工具/data.db "SELECT * FROM user_behavior"

# Windows
sqlite3 %APPDATA%\wx公众号工具\data.db "SELECT * FROM user_behavior"
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `app/models/user_behavior.py` | 用户行为数据模型 |
| `app/services/system.py` | 用户行为管理服务 |
| `app/api/endpoints/system.py` | 用户行为 API 端点 |
| `web/src/views/ArticleList.vue` | 前端使用示例 |

---

*最后更新: 2026-01-08*

