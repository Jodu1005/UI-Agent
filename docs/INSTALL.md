# 安装指南

本文档介绍如何安装和配置 UI-Agent 系统。

## 系统要求

### 硬件要求
- **CPU**: 双核及以上处理器
- **内存**: 4GB RAM 及以上（推荐 8GB）
- **硬盘**: 至少 500MB 可用空间

### 软件要求
- **操作系统**: Windows 10/11（主要支持），macOS/Linux（实验性支持）
- **Python**: 3.10 或更高版本
- **IDE**: PyCharm 2023.2 或更高版本（主要支持）
- **网络**: 需要互联网连接（调用智谱 AI API）

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-org/ui-agent.git
cd ui-agent
```

### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -e .
```

或手动安装依赖：
```bash
pip install pyautogui keyboard pillow mss pyyaml zhipuai pytest pygetwindow
```

**窗口管理功能可选依赖**:
```bash
# Windows 增强功能（推荐）
pip install pywin32 psutil
```

### 依赖说明

| 依赖包 | 用途 | 是否必需 |
|-------|------|----------|
| `pygetwindow` | 跨平台窗口管理 | 是 |
| `pywin32` | Windows API 增强功能 | 否（Windows 推荐） |
| `psutil` | 进程查找功能 | 否 |
| `pyautogui` | GUI 自动化 | 是 |
| `keyboard` | 键盘操作 | 是 |
| `pillow` | 图像处理 | 是 |
| `mss` | 屏幕截图 | 是 |
| `pyyaml` | 配置文件解析 | 是 |
| `zhipuai` | 智谱 AI SDK | 是 |

### 4. 获取 API 密钥

UI-Agent 使用智谱 AI (GLM-4) 进行自然语言理解和视觉定位。

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 进入 API 密钥管理页面
4. 创建新的 API 密钥
5. 复制密钥备用

### 5. 配置环境变量

**Windows (PowerShell):**
```powershell
$env:ZHIPUAI_API_KEY="your_api_key_here"
```

**Windows (CMD):**
```cmd
set ZHIPUAI_API_KEY=your_api_key_here
```

**macOS/Linux:**
```bash
export ZHIPUAI_API_KEY="your_api_key_here"
```

**永久设置（推荐）:**

创建 `.env` 文件在项目根目录：
```bash
ZHIPUAI_API_KEY=your_api_key_here
```

### 6. 验证安装

运行测试命令：

```bash
python -m src.main "帮助"
```

如果安装成功，您应该看到帮助信息输出。

```bash
pytest -m unit
```

运行单元测试验证核心功能。

## 配置文件

### 主配置文件

位置: `config/main.yaml`

```yaml
system:
  log_level: INFO          # 日志级别: DEBUG, INFO, WARNING, ERROR
  log_file: logs/ui_agent.log
  screenshot_dir: screenshots/

ide:
  name: pycharm            # IDE 名称
  version: ">=2023.2"      # 最低版本要求
  config_path: config/operations/pycharm.yaml

api:
  zhipuai:
    api_key: ${ZHIPUAI_API_KEY}  # 从环境变量读取
    model: glm-4v-flash           # 视觉模型
    timeout: 30                    # 请求超时时间（秒）

automation:
  default_timeout: 5.0     # 默认操作超时
  max_retries: 3           # 最大重试次数
  retry_delay: 1.0         # 重试延迟（秒）
  action_delay: 0.2        # 操作间隔（秒）
  coordinate_offset: [36, 46]  # 坐标校准偏移量 [x, y]

safety:
  dangerous_operations:    # 需要确认的危险操作
    - delete_file
    - refactor_rename
  require_confirmation: true   # 是否需要确认
  enable_undo: true           # 是否启用撤销
```

### 坐标校准

由于不同系统的显示缩放和窗口装饰不同，可能需要校准坐标偏移。

1. 首次运行时测试定位准确性
2. 如果定位偏移，调整 `coordinate_offset` 值
3. `[36, 46]` 表示向右偏移 36 像素，向下偏移 46 像素

## 常见问题

### Q: 导入错误 `ModuleNotFoundError`

**A:** 确保虚拟环境已激活，并重新安装依赖：
```bash
pip install -e .
```

### Q: API 调用失败

**A:** 检查以下项目：
1. API 密钥是否正确设置
2. 网络连接是否正常
3. 智谱 AI 账户是否有余额
4. 查看日志文件 `logs/ui_agent.log` 获取详细错误信息

### Q: 坐标定位不准确

**A:** 调整配置中的 `coordinate_offset` 值：
- 如果点击位置偏左/上，增加偏移值
- 如果点击位置偏右/下，减少偏移值

### Q: 权限错误（Windows）

**A:** 某些操作需要管理员权限。以管理员身份运行终端：
- 右键点击终端/PowerShell
- 选择"以管理员身份运行"

### Q: 窗口激活失败

**A:** 如果遇到窗口激活失败的问题，可能是以下原因：

1. **权限不足**：目标应用以管理员权限运行
   - 解决方案：以管理员身份运行 UI-Agent
   - 或关闭目标应用后以普通用户身份重新打开

2. **窗口未找到**：窗口标题不匹配
   - 使用"列出窗口"命令查看可用的窗口标题
   - 确认目标应用正在运行

3. **多显示器问题**：窗口在其他显示器上
   - 确保目标显示器可见
   - 尝试手动将窗口移到主显示器

### Q: pygetwindow 安装失败

**A:** pygetwindow 是窗口管理的核心依赖：

1. 确保使用最新版本的 pip：
   ```bash
   python -m pip install --upgrade pip
   ```

2. 如果 Windows 平台安装失败，尝试：
   ```bash
   pip install pygetwindow>=0.0.9
   ```

3. 验证安装：
   ```bash
   python -c "import pygetwindow; print(pygetwindow.__version__)"
   ```

## 卸载

```bash
deactivate  # 退出虚拟环境
rm -rf .venv  # 删除虚拟环境
# 或手动删除项目目录
```

## 下一步

安装完成后，请阅读 [使用教程](USAGE.md) 了解如何使用 UI-Agent。
