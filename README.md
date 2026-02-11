# 微信公众号爬虫

这是一个用于爬取微信公众号资源的Python项目，支持 **Web API 服务** 和 **桌面应用** 两种运行模式。

## 🎯 项目特色

- 🌐 **Web API模式**：提供 RESTful API 接口，可集成到其他系统
- 💻 **桌面应用模式**：打包成独立可执行文件（.app/.exe），无需安装 Python
- 🔐 **官方接口**：基于微信公众号平台官方接口，数据准确可靠
- 📊 **数据持久化**：支持 MySQL 和 SQLite 两种数据库
- 🎨 **现代前端**：Vue 3 + TypeScript 响应式界面
- 📝 **完整日志**：多级别日志系统，方便调试和监控

## 🚀 快速开始

### 桌面应用（推荐新手使用）

```bash
# 1. 下载并解压应用包
# 2. 双击运行
open dist/wx公众号工具.app   # macOS
# 或
dist\wx公众号工具\wx公众号工具.exe  # Windows
```

**特点**：
- ✅ 无需安装 Python 环境
- ✅ 开箱即用
- ✅ 图形界面操作
- ✅ 数据本地存储

**详细文档**：[公众号爬虫可执行文件流程.md](公众号爬虫可执行文件流程.md)

### Web API 模式（适合开发集成）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd wxPublicCrawl

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env  # 编辑配置文件

# 4. 启动服务
python run_app.py
```

访问 http://localhost:8002 查看 API 文档

## 集成框架

本项目集成了以下框架和库：

1. **FastAPI**: 现代、快速的Web框架，用于构建API。它基于标准的Python类型提示，提供自动文档生成和高性能。

2. **SQLAlchemy**: Python的SQL工具包和ORM框架，提供了SQL抽象层，使得数据库操作更加简单和灵活。

3. **Alembic**: SQLAlchemy的数据库迁移工具，用于管理数据库模式的变更。

4. **MySQL**: 用于数据存储的关系型数据库。

5. **python-dotenv**: 用于从.env文件加载环境变量，方便配置管理。

6. **pydantic-settings**: 基于pydantic的配置管理工具，提供类型安全的配置验证。

7. **pydantic**: 数据验证和设置管理库，使用Python类型注解。

8. **httpx**: 现代化的HTTP客户端，支持异步请求，用于爬取网页内容。

9. **uvicorn**: 现代的ASGI服务器，用于运行FastAPI应用。

10. **cachetools**: 可以方便的进行缓存管理，可以减少数据库查询，提高接口响应速度。

11. **loguru**: 现代化的日志库，支持多种日志级别和格式，方便进行日志管理。

12. **bs4**: 用于解析html，提取标题，方便进行本地化保存。

13. **beautifulsoup4**: 用于解析html，提取标题，方便进行本地化保存。
    
14. **mysql-connector-python**: 用于连接和操作MySQL数据库。

## 项目结构

```
wxPublicCrawl/
├── alembic/              # 数据库迁移相关文件
│   ├── env.py           # Alembic环境配置
│   ├── script.py.mako   # 迁移脚本模板
│   └── versions/        # 迁移版本文件
├── app/                  # 应用程序代码
│   ├── api/              # API路由
│   │   ├── api.py       # API路由集合
│   │   └── endpoints/   # API端点
│   │       └── wx_public.py # 微信公众号接口
│   ├── config/           # 配置模块
│   │   └── database_config.py # 数据库配置（支持 MySQL/SQLite）
│   ├── core/             # 核心配置
│   │   ├── config.py    # 应用配置（支持多环境）
│   │   └── logging_uru.py # 日志配置（Loguru）
│   ├── db/               # 数据库相关
│   │   └── sqlalchemy_db.py # SQLAlchemy数据库连接
│   ├── decorators/       # 装饰器
│   │   └── cache_decorator.py # 缓存装饰器
│   ├── middleware/       # 中间件
│   │   ├── exception_handlers.py # 异常处理器
│   │   └── response_validator.py # 响应验证器
│   ├── models/           # 数据库模型
│   │   └── article.py   # 文章模型
│   ├── schemas/          # Pydantic模型
│   │   ├── wx_data.py   # 微信公众号数据验证模型
│   │   └── common_data.py # 通用数据验证模型
│   ├── scripts/          # 脚本工具
│   │   ├── create_database.py # 创建数据库脚本
│   │   ├── init_database.py  # 初始化数据库脚本
│   │   ├── manage_db.py      # 使用alembic管理数据库脚本
│   │   └── set_env.py        # 环境设置脚本
│   ├── services/         # 业务逻辑服务
│   │   └── wx_public.py # 微信公众号服务
│   ├── utils/            # 工具类
│   │   ├── src_path.py  # 路径处理（桌面应用适配）
│   │   └── wx_article_handle.py # 文章处理
│   ├── __init__.py      # 包初始化文件
│   └── main.py          # 应用入口
│
├── web/                  # 前端代码（Vue 3）
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   │   ├── WeChatLogin.vue   # 登录页
│   │   │   ├── PublicSearch.vue  # 搜索页
│   │   │   └── ArticleList.vue   # 文章列表页
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # 状态管理（Pinia）
│   │   ├── services/    # API 封装
│   │   └── utils/       # 工具函数
│   ├── dist/            # 构建产物（打包时包含）
│   ├── package.json
│   └── vite.config.ts
│
├── script/               # 脚本工具
│   └── desktop/         # 桌面应用脚本
│       ├── build_mac.sh          # macOS 打包
│       ├── build_windows.bat     # Windows 打包
│       ├── test_app.sh           # 测试应用
│       ├── view_logs.sh          # 查看日志
│       ├── kill_app.sh           # 清理应用
│       ├── verify_scripts.sh     # 验证工具
│       ├── README.md             # 脚本说明
│       └── MIGRATION_SUMMARY.md  # 迁移总结
│
├── docs/                 # 文档目录
│   ├── desktop/         # 桌面应用文档
│   │   ├── DESKTOP_APP_GUIDE.md  # 使用指南
│   │   ├── PACKAGING_QUICKSTART.md # 打包快速入门
│   │   └── FIX_*.md              # 问题修复文档
│   └── ...
│
├── dist/                 # 打包输出（生成）
│   ├── wx公众号工具.app        # macOS 应用包
│   └── wx公众号工具/          # 独立可执行文件
│
├── logs/                 # 日志文件目录
├── .env                  # 环境变量配置
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── .env.test             # 测试环境配置
├── alembic.ini           # Alembic配置
├── requirements.txt      # Python 依赖
├── run.sh                # Web API 运行脚本
├── run_app.py            # Web API 启动入口
├── run_desktop.py        # ⭐ 桌面应用启动入口
├── wx_crawler.spec       # ⭐ PyInstaller 打包配置
├── QUICK_REFERENCE.md    # 快速参考卡片
├── 公众号爬虫可执行文件流程.md # ⭐ 桌面应用完整方案
├── .gitignore            # Git 忽略文件
└── README.md             # 本文件
```

**标注说明**：
- ⭐ 桌面应用核心文件
- 📦 打包相关目录
- 🎨 前端相关目录

## 安装和运行

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

本项目支持多环境配置，包括：

- `.env`：默认环境配置
- `.env.development`：开发环境配置
- `.env.test`：测试环境配置
- `.env.production`：生产环境配置

编辑相应的环境配置文件，设置数据库连接信息和其他参数：

```
# 数据库配置
DB_DRIVER=mysql+mysqlconnector
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wx_public_dev
DB_CHARSET=utf8mb4

# API配置
API_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development
```

### 4. 数据库操作

#### 4.1 创建数据库

在使用应用前，需要先创建数据库。可以使用`app/scripts/create_database.py`脚本：

```bash
python -m app.scripts.create_database
或者
python -m app.scripts.set_env dev create_db
```

该脚本会根据环境配置文件中的数据库设置创建数据库。

#### 4.2 初始化数据库表

创建数据库后，需要初始化数据库表结构。有两种方式：

**方式一：使用SQLAlchemy直接创建表**

```bash
python -m app.scripts.init_database
```

该脚本会使用SQLAlchemy的`create_all()`方法创建所有在`app/models`目录下定义的模型对应的表。

**方式二：使用Alembic进行数据库迁移（推荐）**

```bash
# 创建迁移脚本
alembic revision --autogenerate -m "创建初始表结构"

# 应用迁移
alembic upgrade head
```
> 或者使用set_env.py脚本去管理数据库，创建迁移脚本，应用迁移，回滚迁移。内部使用manage_db.py脚本调用alembic命令

```bash
# 创建迁移脚本
python -m app.scripts.set_env dev migrate revision --autogenerate -m "pro_table"

# 应用迁移
python -m app.scripts.set_env dev upgrade

# 回滚迁移
python -m app.scripts.set_env dev downgrade
```

#### 4.3 数据库字段更新

> 当模型定义发生变化时（如添加、修改或删除字段），使用Alembic进行数据库迁移：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "更新字段描述"

# 应用迁移
alembic upgrade head

# 回滚迁移（如需要）
alembic downgrade -1  # 回滚一个版本
```
> 或者使用set_env.py脚本去管理数据库，创建迁移脚本，应用迁移，回滚迁移。内部使用manage_db.py脚本调用alembic命令

```bash
# 创建迁移脚本
python -m app.scripts.set_env dev migrate revision --autogenerate -m "pro_table"

# 应用迁移
python -m app.scripts.set_env dev upgrade

# 回滚迁移
python -m app.scripts.set_env dev downgrade
```

Alembic会自动检测模型变化并生成相应的迁移脚本，然后可以应用或回滚这些变化。

### 5. 运行应用

有两种方式运行应用：

**方式一：使用run.sh脚本（推荐）**

```bash
./run.sh
```

该脚本会自动创建虚拟环境、安装依赖并启动应用。脚本内容如下：

```bash
#!/bin/bash

# 创建并激活虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 运行应用
echo "启动应用..."
python run_app.py
```

**方式二：直接运行Python脚本**

```bash
python run_app.py
```

`run_app.py`脚本会确保项目根目录被添加到Python路径中，以便正确导入应用模块：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 添加项目根目录到python的路径
import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    import logging
    
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)
```

应用将在 http://localhost:8002 运行，API文档可在 http://localhost:8002/docs 访问。

## 桌面应用打包

### 打包环境准备

```bash
# 1. 安装打包依赖
pip install pyinstaller pywebview filelock

# 2. 构建前端
cd web
npm install
npm run build:only
cd ..
```

### 打包命令

**macOS**:

```bash
script/desktop/build_mac.sh
```

**Windows**:

```batch
script\desktop\build_windows.bat
```

### 打包输出

```
dist/
├── wx公众号工具.app        # macOS 应用包
└── wx公众号工具/          # 独立可执行文件
    ├── _internal/            # 依赖文件
    └── wx公众号工具       # 可执行文件 (macOS)
                              # 或 wx公众号工具.exe (Windows)
```

### 桌面应用特性

| 特性 | 说明 |
|------|------|
| **运行模式** | 独立可执行文件，无需 Python 环境 |
| **数据库** | 使用 SQLite，数据保存在用户目录 |
| **端口** | 固定使用 18000 |
| **单实例** | 自动防止多开 |
| **日志位置** | macOS: `~/Library/Logs/wx公众号工具/`<br/>Windows: `~/AppData/Local/wx公众号工具/Logs/` |
| **数据位置** | macOS: `~/Library/Application Support/wx公众号工具/`<br/>Windows: `~/AppData/Local/wx公众号工具/` |

### 桌面应用管理

```bash
# 查看日志
script/desktop/view_logs.sh

# 测试应用
script/desktop/test_app.sh

# 清理应用
script/desktop/kill_app.sh

# 验证脚本
script/desktop/verify_scripts.sh
```

### 相关文档

- [公众号爬虫可执行文件流程.md](公众号爬虫可执行文件流程.md) - 完整设计方案
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考卡片
- [docs/desktop/](docs/desktop/) - 详细文档目录
- [script/desktop/README.md](script/desktop/README.md) - 脚本使用说明

## API接口

### 搜索微信公众号文章

```
GET /api/v1/wx/search?query=关键词
```

此接口会调用搜狗微信搜索，获取相关的微信公众号文章信息。

## 日志系统

本项目集成了完善的日志系统，支持控制台彩色输出和文件记录：

- **日志配置**：在`app/core/logging.py`中配置
- **日志级别**：根据DEBUG环境变量自动调整（DEBUG模式下为DEBUG级别，否则为INFO级别）
- **日志格式**：包含时间、日志名称、级别和消息，不同级别使用不同颜色显示
- **日志输出**：同时输出到控制台和`logs`目录下的日期命名文件（如`app_2025-05-16.log`）

## 环境隔离与切换

### Python虚拟环境

本项目使用Python虚拟环境进行环境隔离，确保项目依赖不会影响系统全局Python环境。虚拟环境的创建和激活方法如下：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在Linux/macOS上
source venv/bin/activate
# 在Windows上
venv\Scripts\activate
```

### python-dotenv环境切换

本项目使用python-dotenv库实现不同环境（开发、测试、生产）的配置隔离和切换。环境切换的实现方式如下：

1. **环境配置文件**：
   - `.env`：默认环境配置
   - `.env.development`：开发环境配置
   - `.env.test`：测试环境配置
   - `.env.production`：生产环境配置

2. **环境切换机制**：
   在`app/core/config.py`中，通过设置`ENV`环境变量来切换不同的环境配置：

   ```python
   # 获取当前环境
   ENV = os.getenv("ENV", "development")
   
   # 根据环境选择配置文件
   env_file = ".env"
   if ENV == "prod":
       env_file = ".env.production"
   elif ENV == "test":
       env_file = ".env"
   elif ENV == "dev":
       env_file = ".env.development"
       
   # 加载环境配置
   load_dotenv(env_file, override=True)
   ```
    使用：
    ```bash
    python -m app.scripts.set_env dev
    或者
    python -m app.scripts.set_env test
    或者
    python -m app.scripts.set_env prod
    ```

3. **切换环境的方法**：
   - 通过设置环境变量：`export ENV=prod`（Linux/macOS）或`set ENV=prod`（Windows）
   - 通过脚本设置：在`app/scripts/set_env.py`中可以编程方式设置环境
   - 在运行脚本中设置：如`os.environ["ENV"] = "production"`

## 使用场景

### Web API 模式适用于：

- 🔌 需要集成到现有系统
- 🌐 提供 REST API 服务
- 🐳 Docker 容器化部署
- 📊 数据采集和分析平台
- 🔄 需要与其他服务交互

### 桌面应用模式适用于：

- 👥 个人使用或小团队
- 💻 无需服务器环境
- 🔒 数据本地存储
- 🎨 需要图形界面
- 📱 快速上手使用

## 常见问题

### Q: 如何选择使用模式？

**A**: 
- 如果你是开发者，需要集成API → 使用 **Web API 模式**
- 如果你想快速使用，不懂编程 → 使用 **桌面应用模式**

### Q: 桌面应用如何更新？

**A**: 重新下载最新版本，旧版本的数据会自动迁移（数据保存在用户目录）

### Q: 数据保存在哪里？

**A**: 
- Web API 模式：MySQL 数据库
- 桌面应用：SQLite 数据库（用户目录）
  - macOS: `~/Library/Application Support/wx公众号工具/`
  - Windows: `~/AppData/Local/wx公众号工具/`

### Q: 桌面应用可以同时打开多个吗？

**A**: 不可以，应用会自动检测并防止多开（单实例模式）

## 技术栈总览

### 后端
- **框架**: FastAPI 
- **数据库**: SQLAlchemy + MySQL/SQLite
- **异步**: httpx, asyncio
- **日志**: Loguru
- **迁移**: Alembic

### 前端  
- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **样式**: TailwindCSS + UnoCSS
- **状态**: Pinia
- **路由**: Vue Router

### 桌面
- **容器**: PyWebView
- **打包**: PyInstaller
- **进程**: multiprocessing
- **锁机制**: filelock

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 更新日志

### v1.0.0 (2025-12-22)
- ✅ 完成桌面应用打包
- ✅ 支持 macOS 和 Windows
- ✅ 实现单实例控制
- ✅ SQLite 数据库适配
- ✅ 完善文档和脚本

### v0.9.0 (2024-XX-XX)
- ✅ 实现 Web API 基础功能
- ✅ 微信登录流程
- ✅ 公众号搜索
- ✅ 文章列表和详情

## 许可证

MIT License

Copyright (c) 2025 wxPublicCrawl Team

---

**⚠️ 免责声明**：本工具仅供学习和研究使用，请勿用于商业用途。使用本工具所产生的一切后果由使用者自行承担。
