# LLM配置管理接口使用说明

## 概述

新增了LLM配置管理功能，支持从数据库管理多个AI模型配置，实现模型的动态切换和管理。

## 主要特性

1. **统一格式**：所有接口返回统一的 `ApiResponseData` 格式
2. **统一请求方式**：所有接口都使用 POST 请求
3. **数据库存储**：AI模型配置存储在数据库中，支持持久化
4. **多配置管理**：可以创建多个配置，支持激活状态切换
5. **用户隔离**：支持全局配置和用户专属配置
6. **模型类型枚举**：主要支持 GPT、Claude、Qwen、GLM、DeepSeek、Gemini

## API接口列表

所有接口都使用 POST 请求，返回统一的 `ApiResponseData` 格式：

```json
{
  "platform": "WX_PUBLIC",
  "api": "接口名称",
  "data": {...},
  "ret": [],
  "v": 1
}
```

### 1. 创建LLM配置

**接口**: `POST /api/wx/public/llm-config/llm-config-create`

**请求体**:
```json
{
  "user_id": null,
  "model_type": "GPT",
  "model_name": "gpt-4-turbo",
  "ai_api_key": "your-api-key-here",
  "ai_base_url": "https://api.openai.com/v1",
  "api_endpoint": null,
  "temperature": 70,
  "max_tokens": 2000,
  "top_p": null,
  "enable_history": true,
  "max_history": 10,
  "enable_stream": false,
  "system_prompt": "You are a helpful assistant.",
  "custom_parameters": null,
  "description": "GPT-4 Turbo 配置",
  "is_active": true
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-create",
  "data": {
    "id": 1,
    "user_id": null,
    "is_active": true,
    "model_type": "GPT",
    "model_name": "gpt-4-turbo",
    "ai_api_key": "your-api-key-here",
    "ai_base_url": "https://api.openai.com/v1",
    "api_endpoint": null,
    "temperature": 70,
    "max_tokens": 2000,
    "top_p": null,
    "enable_history": true,
    "max_history": 10,
    "enable_stream": false,
    "system_prompt": "You are a helpful assistant.",
    "custom_parameters": null,
    "description": "GPT-4 Turbo 配置",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "ret": [],
  "v": 1
}
```

### 2. 获取配置列表

**接口**: `POST /api/wx/public/llm-config/llm-config-list`

**请求体**:
```json
{
  "user_id": null,
  "model_type": "GPT",
  "is_active": true,
  "skip": 0,
  "limit": 10
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-list",
  "data": {
    "total": 1,
    "items": [
      {
        "id": 1,
        "user_id": null,
        "is_active": true,
        "model_type": "GPT",
        "model_name": "gpt-4-turbo",
        "ai_api_key": "your-a...ere",
        "ai_base_url": "https://api.openai.com/v1",
        "api_endpoint": null,
        "temperature": 70,
        "max_tokens": 2000,
        "top_p": null,
        "enable_history": true,
        "max_history": 10,
        "enable_stream": false,
        "system_prompt": "You are a helpful assistant.",
        "custom_parameters": null,
        "description": "GPT-4 Turbo 配置",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "ret": [],
  "v": 1
}
```

### 3. 获取单个配置

**接口**: `POST /api/wx/public/llm-config/llm-config-get`

**请求体**:
```json
{
  "config_id": 1,
  "user_id": null
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-get",
  "data": {
    "id": 1,
    "user_id": null,
    "is_active": true,
    "model_type": "GPT",
    "model_name": "gpt-4-turbo",
    "ai_api_key": "your-api-key-here",
    "ai_base_url": "https://api.openai.com/v1",
    ...
  },
  "ret": [],
  "v": 1
}
```

### 4. 更新配置

**接口**: `POST /api/wx/public/llm-config/llm-config-update`

**请求体**:
```json
{
  "config_id": 1,
  "user_id": null,
  "temperature": 80,
  "max_tokens": 4000,
  "is_active": false
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-update",
  "data": {
    "id": 1,
    ...
    "temperature": 80,
    "max_tokens": 4000,
    "is_active": false,
    ...
  },
  "ret": [],
  "v": 1
}
```

### 5. 删除配置

**接口**: `POST /api/wx/public/llm-config/llm-config-delete`

**请求体**:
```json
{
  "config_id": 1,
  "user_id": null
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-delete",
  "data": {
    "success": true,
    "message": "删除成功"
  },
  "ret": [],
  "v": 1
}
```

### 6. 获取当前激活配置

**接口**: `POST /api/wx/public/llm-config/llm-config-active`

**请求体**:
```json
{
  "user_id": null
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-active",
  "data": {
    "id": 1,
    "user_id": null,
    "is_active": true,
    "model_type": "GPT",
    "model_name": "gpt-4-turbo",
    "ai_api_key": "your-a...ere",
    "ai_base_url": "https://api.openai.com/v1",
    ...
  },
  "ret": [],
  "v": 1
}
```

### 7. 切换激活配置

**接口**: `POST /api/wx/public/llm-config/llm-config-switch`

**请求体**:
```json
{
  "config_id": 2,
  "user_id": null
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-switch",
  "data": {
    "id": 2,
    "is_active": true,
    ...
  },
  "ret": [],
  "v": 1
}
```

### 8. 获取支持的模型类型

**接口**: `POST /api/wx/public/llm-config/llm-config-model-types`

**请求体**: 不需要（可传空对象 `{}`）

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-model-types",
  "data": {
    "model_types": [
      "GPT",
      "Claude",
      "Qwen",
      "GLM",
      "DeepSeek",
      "Gemini",
      "Custom"
    ]
  },
  "ret": [],
  "v": 1
}
```

### 9. 获取客户端配置

**接口**: `POST /api/wx/public/llm-config/llm-config-client`

**请求体**:
```json
{
  "user_id": null
}
```

**响应**:
```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-client",
  "data": {
    "api_key": "your-api-key-here",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    "enable_history": true,
    "max_history": 10,
    "system_prompt": "You are a helpful assistant."
  },
  "ret": [],
  "v": 1
}
```

## 前端调用示例

### 使用 fetch

```javascript
// 创建配置
const createConfig = async () => {
  const response = await fetch('http://localhost:8002/api/wx/public/llm-config/llm-config-create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model_type: 'GPT',
      model_name: 'gpt-4-turbo',
      ai_api_key: 'your-api-key',
      ai_base_url: 'https://api.openai.com/v1',
      is_active: true
    })
  });
  const result = await response.json();
  console.log(result);
};

// 获取配置列表
const getConfigList = async () => {
  const response = await fetch('http://localhost:8002/api/wx/public/llm-config/llm-config-list', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: null,
      skip: 0,
      limit: 10
    })
  });
  const result = await response.json();
  console.log(result);
};

// 切换配置
const switchConfig = async (configId) => {
  const response = await fetch('http://localhost:8002/api/wx/public/llm-config/llm-config-switch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      config_id: configId,
      user_id: null
    })
  });
  const result = await response.json();
  console.log(result);
};
```

### 使用 axios

```javascript
import axios from 'axios';

// 创建配置
const createConfig = async () => {
  const response = await axios.post(
    'http://localhost:8002/api/wx/public/llm-config/llm-config-create',
    {
      model_type: 'GPT',
      model_name: 'gpt-4-turbo',
      ai_api_key: 'your-api-key',
      ai_base_url: 'https://api.openai.com/v1',
      is_active: true
    }
  );
  console.log(response.data);
};

// 获取配置列表
const getConfigList = async () => {
  const response = await axios.post(
    'http://localhost:8002/api/wx/public/llm-config/llm-config-list',
    {
      user_id: null,
      skip: 0,
      limit: 10
    }
  );
  console.log(response.data);
};
```

## 错误处理

所有接口返回的 `ret` 数组中包含错误信息：

```json
{
  "platform": "WX_PUBLIC",
  "api": "llm-config-get",
  "data": null,
  "ret": ["配置不存在"],
  "v": 1
}
```

前端应该检查 `ret` 数组是否为空：
- 如果 `ret` 为空数组 `[]`，表示操作成功
- 如果 `ret` 包含错误信息，表示操作失败

## 配置优先级

1. **用户激活配置**：如果提供了 `user_id`，优先使用该用户的激活配置
2. **全局激活配置**：如果用户没有激活配置，使用全局激活配置
3. **配置文件默认值**：如果数据库中没有配置，回退到配置文件中的默认值（`settings.AI_API_KEY` 等）

## 模型类型

支持的模型类型：
- **GPT**: OpenAI GPT系列
- **Claude**: Anthropic Claude系列
- **Qwen**: 阿里通义千问
- **GLM**: 智谱GLM系列
- **DeepSeek**: DeepSeek系列
- **Gemini**: Google Gemini
- **Custom**: 自定义模型

## API密钥脱敏

为了安全，所有列表和查询接口返回的API密钥都是脱敏的（只显示前6位和后4位）。

完整API密钥只在创建配置和获取单个配置的完整信息时会返回（请妥善保管）。

## 注意事项

1. **激活状态唯一性**：同一级别（全局或用户）只能有一个激活的配置
2. **配置切换**：切换激活配置时，会自动取消其他配置的激活状态
3. **数据库连接**：使用数据库配置功能需要确保数据库已正确初始化
4. **兼容性**：如果不设置 `use_db_config=True`，仍然会使用配置文件中的默认值
5. **统一格式**：所有接口都返回 `ApiResponseData` 格式，前端需要统一解析
6. **POST请求**：所有接口都使用 POST 请求，即使获取数据也是如此

## 在代码中使用

### 1. 使用数据库配置创建AI客户端

```python
from app.ai.llm.ai_client import AIClient, create_default_client

# 方式1: 直接创建客户端
client = AIClient(
    use_db_config=True,  # 从数据库获取配置
    user_id=None,       # 用户ID（None表示使用全局配置）
    enable_history=True
)

# 方式2: 使用便捷函数
client = create_default_client(
    use_db_config=True,
    user_id="user123"
)
```

### 2. 手动获取配置

```python
from app.db.sqlalchemy_db import get_sqlalchemy_db
from app.services.llm_configuration import get_llm_config_for_client

db = get_sqlalchemy_db()
try:
    config = get_llm_config_for_client(db, user_id="user123")
    print(config)
    # 输出: {
    #   "api_key": "...",
    #   "base_url": "...",
    #   "model": "gpt-4-turbo",
    #   "temperature": 0.7,
    #   "max_tokens": 2000,
    #   ...
    # }
finally:
    db.close()
```

## 数据库迁移

首次使用时，数据库表会自动创建（SQLite模式下）。如果使用其他数据库，需要手动执行迁移脚本或确保表结构已创建。

表名：`llm_configuration`
