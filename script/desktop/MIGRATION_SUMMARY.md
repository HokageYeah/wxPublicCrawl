# 脚本迁移总结

## 📦 迁移内容

所有桌面应用相关的脚本已从项目根目录迁移到 `script/desktop/` 目录。

## 🔄 变更概览

### 文件迁移

| 原位置 | 新位置 | 状态 |
|--------|--------|------|
| `./build_mac.sh` | `script/desktop/build_mac.sh` | ✅ 已迁移并适配 |
| `./build_windows.bat` | `script/desktop/build_windows.bat` | ✅ 已迁移并适配 |
| `./kill_app.sh` | `script/desktop/kill_app.sh` | ✅ 已迁移（无需修改） |
| `./test_app.sh` | `script/desktop/test_app.sh` | ✅ 已迁移并适配 |
| `./view_logs.sh` | `script/desktop/view_logs.sh` | ✅ 已迁移（无需修改） |

### 新增文件

| 文件 | 说明 |
|------|------|
| `script/desktop/README.md` | 脚本使用说明文档 |
| `script/desktop/verify_scripts.sh` | 脚本验证工具 |
| `script/desktop/MIGRATION_SUMMARY.md` | 本文件 |

## 🔧 技术修改

### 1. 自动路径切换

所有需要访问项目文件的脚本都添加了自动路径切换逻辑：

**macOS/Linux (bash)**:

```bash
# ============================================================================
# 自动切换到项目根目录
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

**Windows (bat)**:

```batch
REM ============================================================================
REM 自动切换到项目根目录
REM ============================================================================
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%..\.."
set "PROJECT_ROOT=%CD%"
```

### 2. 脚本互相引用

修改了脚本之间的调用路径：

**test_app.sh**:

```bash
# 原来：./kill_app.sh
# 现在：
"$SCRIPT_DIR/kill_app.sh"
```

### 3. 文档更新

更新了以下文档中的路径引用：

- `QUICK_REFERENCE.md`
- `DESKTOP_APP_GUIDE.md`
- 其他相关文档

## ✅ 验证结果

运行验证脚本：

```bash
script/desktop/verify_scripts.sh
```

**结果**：✅ 所有检查通过（17/17）

- ✅ 所有脚本文件存在且可执行
- ✅ 项目文件结构完整
- ✅ 路径切换逻辑正确
- ✅ 可从任意位置运行脚本

## 🚀 使用方式

### 方式1：直接运行（推荐）

```bash
# 从项目根目录
cd /path/to/wxPublicCrawl
script/desktop/build_mac.sh

# 或从脚本目录
cd script/desktop
./build_mac.sh

# 或从任意位置
/path/to/wxPublicCrawl/script/desktop/build_mac.sh
```

### 方式2：创建符号链接（可选）

如果希望保持旧的使用习惯，可以在项目根目录创建符号链接：

```bash
cd /path/to/wxPublicCrawl

# 创建符号链接
ln -s script/desktop/build_mac.sh build_mac.sh
ln -s script/desktop/kill_app.sh kill_app.sh
ln -s script/desktop/test_app.sh test_app.sh
ln -s script/desktop/view_logs.sh view_logs.sh

# 然后就可以像以前一样使用
./build_mac.sh
./test_app.sh
```

## 📋 迁移优势

### 1. 更好的组织结构

```
wxPublicCrawl/
├── script/
│   └── desktop/          # 所有桌面脚本集中管理
│       ├── build_mac.sh
│       ├── build_windows.bat
│       ├── kill_app.sh
│       ├── test_app.sh
│       ├── view_logs.sh
│       ├── verify_scripts.sh
│       ├── README.md
│       └── MIGRATION_SUMMARY.md
├── app/                  # 后端代码
├── web/                  # 前端代码
└── ...                   # 其他项目文件
```

### 2. 清晰的职责划分

- **项目根目录**：只保留核心配置文件（`requirements.txt`、`wx_crawler.spec`、`run_desktop.py` 等）
- **script/desktop/**：所有构建和管理脚本
- **app/**：后端代码
- **web/**：前端代码

### 3. 易于扩展

未来可以添加更多脚本目录：

```
script/
├── desktop/       # 桌面应用脚本
├── deploy/        # 部署脚本
├── test/          # 测试脚本
└── utils/         # 工具脚本
```

### 4. 减少根目录混乱

- **迁移前**：根目录有 5+ 个 `.sh` 脚本文件
- **迁移后**：脚本整齐地归类在 `script/desktop/` 目录

## 🔍 兼容性

### 完全兼容

- ✅ 所有脚本功能完全相同
- ✅ 可从任意位置运行
- ✅ 自动处理路径问题
- ✅ 输出目录不变（`dist/`、`build/`）

### 需要更新的地方

1. **CI/CD 配置**（如果有）：

```yaml
# 原来
- run: ./build_mac.sh

# 现在
- run: script/desktop/build_mac.sh
```

2. **开发文档**：

已更新以下文档：
- ✅ `QUICK_REFERENCE.md`
- ✅ `DESKTOP_APP_GUIDE.md`
- ✅ `script/desktop/README.md`

3. **个人习惯**：

如果习惯在根目录运行 `./build_mac.sh`，可以：
- 选项A：改用 `script/desktop/build_mac.sh`
- 选项B：创建符号链接（见上文"方式2"）

## 🎯 最佳实践

### 推荐做法

```bash
# 1. 直接使用新路径（推荐）
script/desktop/build_mac.sh
script/desktop/test_app.sh
script/desktop/view_logs.sh

# 2. 添加到 PATH（高级）
export PATH="$PATH:$(pwd)/script/desktop"
build_mac.sh
test_app.sh
```

### 不推荐

```bash
# ❌ 创建过多符号链接（会使根目录又变乱）
ln -s script/desktop/* .

# ❌ 复制脚本文件（会导致维护问题）
cp script/desktop/build_mac.sh .
```

## 📚 相关文档

- [script/desktop/README.md](./README.md) - 脚本使用详细说明
- [../../QUICK_REFERENCE.md](../../QUICK_REFERENCE.md) - 快速参考
- [../../DESKTOP_APP_GUIDE.md](../../DESKTOP_APP_GUIDE.md) - 桌面应用指南

## 🔧 故障排除

### 问题1：脚本找不到文件

**症状**：

```
./build_mac.sh: line 58: cd: web: No such file or directory
```

**原因**：使用旧版本的脚本（未更新路径切换逻辑）

**解决**：

```bash
# 重新拉取最新脚本
git pull
# 或手动更新脚本
```

### 问题2：脚本不可执行

**症状**：

```
-bash: script/desktop/build_mac.sh: Permission denied
```

**解决**：

```bash
chmod +x script/desktop/*.sh
```

### 问题3：Windows 路径问题

**症状**：

```
系统找不到指定的路径
```

**解决**：

```batch
REM 确保使用正确的路径分隔符
script\desktop\build_windows.bat
```

## ✅ 验证迁移

运行以下命令验证所有修改正确：

```bash
# 1. 验证脚本
script/desktop/verify_scripts.sh

# 2. 测试构建（可选）
script/desktop/build_mac.sh

# 3. 测试应用（可选）
script/desktop/test_app.sh
```

## 📅 迁移时间线

- **2025-12-22**：完成脚本迁移
- **2025-12-22**：更新所有文档
- **2025-12-22**：添加验证工具
- **2025-12-22**：验证通过 ✅

---

**迁移负责人**：AI Assistant  
**迁移日期**：2025-12-22  
**状态**：✅ 完成并验证

