# AI模块使用文档

本模块提供了可扩展的AI客户端和提示词管理功能，方便在项目中集成各种AI能力。

## 📁 目录结构

```
app/ai/
├── code/
│   ├── ai_client.py           # AI客户端基础类
│   ├── prompt_manager.py      # 提示词管理类
│   └── education_analyze.py   # 教育内容分析（使用示例）
├── prompt/
│   └── education_prompt.txt   # 教育分析提示词模板
└── README.md                  # 本文档
```

## 🚀 快速开始

### 0. 环境配置

在使用前，请确保已配置AI相关环境变量：

**方法1: 使用 .env 文件（推荐）**

在项目根目录创建 `.env.desktop` 或 `.env` 文件：

```bash
# AI配置
AI_API_KEY=your-openai-api-key
AI_BASE_URL=https://api.openai.com/v1  # 可选，使用代理时配置
AI_MODEL=gpt-3.5-turbo
```

**方法2: 设置环境变量**

```bash
export AI_API_KEY="your-openai-api-key"
export AI_MODEL="gpt-3.5-turbo"
```

**快速测试配置是否正确：**

```bash
# 在项目根目录运行
python app/ai/test/quick_test.py
```

### 1. 基础使用 - AI客户端

#### 简单对话

```python
from app.ai.llm.ai_client import AIClient

# 创建AI客户端
client = AIClient()

# 发送消息
response = await client.chat(
    user_message="请帮我分析一下这段文字的情感倾向",
    system_message="你是一个专业的文本分析助手"
)
print(response)
```

#### JSON格式响应

```python
# 期望返回JSON格式
result = await client.chat_with_json_response(
    user_message="请返回 {'sentiment': 'positive'} 格式",
    temperature=0.1
)
# 自动解析为Python对象
print(result['sentiment'])
```

#### 流式响应（实时显示）

```python
async for chunk in client.stream_chat(
    user_message="写一首关于春天的诗",
    system_message="你是一个诗人"
):
    print(chunk, end='', flush=True)
```

### 2. 提示词管理

#### 加载和渲染提示词

```python
from app.ai.utils.prompt_manager import get_prompt_manager

# 获取全局提示词管理器（单例）
manager = get_prompt_manager()

# 加载提示词模板（从 app/ai/prompt/education_prompt.txt）
manager.load_prompt("education_prompt", "education_prompt.txt")

# 渲染提示词
prompt = manager.render_prompt(
    "education_prompt",
    articles_json='[{"id": "1", "title": "小学数学教学方法"}]'
)
```

#### 便捷函数

```python
from app.ai.utils.prompt_manager import load_and_render_prompt

# 一步完成加载和渲染
prompt = load_and_render_prompt(
    "education_prompt",
    articles_json='[...]'
)
```

#### 动态构建提示词

```python
from app.ai.utils.prompt_manager import PromptBuilder

prompt = (PromptBuilder()
    .add_system_context("你是一个专业的数据分析师")
    .add_instruction("分析以下销售数据")
    .add_data(sales_data, label="销售数据")
    .add_constraints([
        "只返回JSON格式",
        "包含总销售额和趋势分析"
    ])
    .build())
```

### 3. 实战示例 - 教育内容分析

查看 `education_analyze.py` 了解完整实现：

```python
from app.ai.code.education_analyze import analyze_education_articles
from app.schemas.wx_data import ArticleSimple

# 准备文章列表
articles = [
    ArticleSimple(aid="1", title="小学数学教学方法探讨"),
    ArticleSimple(aid="2", title="今日天气预报"),
    ArticleSimple(aid="3", title="高考志愿填报指南")
]

# 分析哪些是教育相关
education_aids = await analyze_education_articles(articles)
# 返回: ["1", "3"]
```

## 🔧 高级配置

### 自定义AI客户端

```python
from app.ai.llm.ai_client import AIClient

client = AIClient(
    api_key="your-api-key",           # 覆盖默认配置
    base_url="https://api.openai.com/v1",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    enable_history=True,               # 启用对话历史
    max_history=10                     # 保留最近10条对话
)
```

### 使用对话历史

```python
# 第一次对话
response1 = await client.chat(
    user_message="我叫张三",
    use_history=True  # 保存到历史
)

# 第二次对话（AI会记住之前的内容）
response2 = await client.chat(
    user_message="我叫什么名字？",
    use_history=True
)
# AI会回答：你叫张三

# 清空历史
client.clear_history()
```

### 自定义提示词目录

```python
from app.ai.utils.prompt_manager import PromptManager

# 使用自定义目录
manager = PromptManager(prompt_dir="/path/to/prompts")
```

## 🎯 扩展方向

### 1. RAG（检索增强生成）- 待实现

```python
# 未来接口示例
response = await client.chat_with_retrieval(
    user_message="微信公众号如何认证？",
    top_k=5  # 从向量数据库检索5条相关文档
)
```

**实现步骤：**
1. 集成向量数据库（Pinecone、Weaviate、Milvus等）
2. 实现文档向量化和存储
3. 在 `ai_client.py` 中实现 `chat_with_retrieval` 方法

### 2. 函数调用（Function Calling）- 待实现

```python
# 未来接口示例
functions = [
    {
        "name": "get_weather",
        "description": "获取天气信息",
        "parameters": {...}
    }
]

result = await client.chat_with_function_calling(
    user_message="北京今天天气怎么样？",
    functions=functions
)
```

### 3. 提示词版本管理 - 待实现

```python
# 未来接口示例
# 使用特定版本的提示词（用于A/B测试）
template_v1 = manager.get_prompt_with_version("education_prompt", "v1.0")
template_v2 = manager.get_prompt_with_version("education_prompt", "v2.0")
```

### 4. 多模态支持 - 待实现

```python
# 未来接口示例
response = await client.chat_with_image(
    user_message="这张图片里有什么？",
    image_url="https://example.com/image.jpg"
)
```

## 📝 提示词模板语法

提示词文件使用 Jinja2 模板语法：

```text
你是一个{{ role }}。
请分析以下数据：
{{ data }}

{% if include_examples %}
示例：
{% for example in examples %}
- {{ example }}
{% endfor %}
{% endif %}
```

使用：

```python
prompt = manager.render_prompt(
    "my_prompt",
    role="数据分析师",
    data="...",
    include_examples=True,
    examples=["示例1", "示例2"]
)
```

## 🎨 最佳实践

### 1. 使用单例模式管理提示词

```python
# ✅ 推荐：使用全局单例
from app.ai.utils.prompt_manager import get_prompt_manager
manager = get_prompt_manager()

# ❌ 不推荐：每次创建新实例
manager = PromptManager()  # 会丢失缓存
```

### 2. 合理设置temperature

```python
# 分类、提取等任务：使用低temperature
client = AIClient(temperature=0.1)

# 创作、聊天等任务：使用中等temperature
client = AIClient(temperature=0.7)

# 创意写作：使用高temperature
client = AIClient(temperature=1.0)
```

### 3. 错误处理

```python
try:
    result = await client.chat(user_message="...")
except ValueError as e:
    # 处理JSON解析错误
    logger.error(f"JSON解析失败: {e}")
except FileNotFoundError as e:
    # 处理提示词文件不存在
    logger.error(f"提示词未找到: {e}")
except Exception as e:
    # 处理其他错误
    logger.error(f"AI调用失败: {e}")
```

### 4. 日志记录

AI客户端和提示词管理器都使用 `loguru` 记录日志：

- INFO: 正常操作日志
- WARNING: 非预期情况（如JSON格式不正确）
- ERROR: 错误信息

## 🔍 调试技巧

### 查看实际发送的提示词

```python
# 渲染提示词后先打印查看
prompt = manager.render_prompt("my_prompt", data="...")
print("="*50)
print(prompt)
print("="*50)

# 再发送给AI
response = await client.chat(user_message=prompt)
```

### 查看对话历史

```python
client = AIClient(enable_history=True)
# ... 多轮对话 ...
history = client.get_history()
for msg in history:
    print(f"{msg['role']}: {msg['content'][:50]}...")
```

## 🧪 运行示例

### 快速测试

```bash
# 在项目根目录运行快速测试
python app/ai/test/quick_test.py
```

这将测试：
- AI配置是否正确
- AI客户端是否可用
- JSON响应功能
- 提示词管理器

### 运行完整示例

```bash
# 方法1: 直接运行（推荐）
python app/ai/test/usage_examples.py

# 方法2: 作为模块运行
python -m app.ai.test.usage_examples
```

### 运行单个示例

在 `test/usage_examples.py` 文件末尾修改：

```python
if __name__ == "__main__":
    # 运行单个示例
    asyncio.run(example_basic_chat())
```

## 📚 相关文档

- [OpenAI API文档](https://platform.openai.com/docs/api-reference)
- [Jinja2模板文档](https://jinja.palletsprojects.com/)
- [项目主README](../../README.md)

## 🤝 贡献

添加新的AI功能时，请遵循以下规范：

1. 在 `ai_client.py` 中添加新方法（如果是通用AI能力）
2. 在 `code/` 目录下创建具体业务模块（如 `sentiment_analyze.py`）
3. 在 `prompt/` 目录下添加对应的提示词文件
4. 更新本文档的使用示例

## 📄 许可证

本项目使用的许可证与主项目相同。

