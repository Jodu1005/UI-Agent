# 故障排除指南

本文档提供 UI-Agent 常见问题的诊断和解决方案。

## 目录

- [安装问题](#安装问题)
- [配置问题](#配置问题)
- [API 调用问题](#api-调用问题)
- [UI 定位问题](#ui-定位问题)
- [自动化执行问题](#自动化执行问题)
- [性能问题](#性能问题)
- [调试技巧](#调试技巧)

## 安装问题

### 依赖安装失败

**症状**: `pip install` 失败或出现权限错误

**解决方案**:

1. 确保使用虚拟环境：
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# 或
source .venv/bin/activate  # macOS/Linux
```

2. 使用 `--user` 标志（仅限系统 Python）：
```bash
pip install --user pyautogui keyboard pillow mss pyyaml zhipuai
```

3. 升级 pip：
```bash
python -m pip install --upgrade pip
```

---

### Python 版本不兼容

**症状**: 导入错误或语法错误

**解决方案**: 确保使用 Python 3.10+

```bash
python --version
```

如果版本低于 3.10，请从 [python.org](https://www.python.org/) 下载新版本。

---

### macOS 权限问题

**症状**: 无法控制鼠标或键盘

**解决方案**:授予辅助功能权限

1. 打开"系统偏好设置" > "安全性与隐私" > "隐私"
2. 选择"辅助功能"
3. 添加 Python 或终端应用

## 配置问题

### 配置文件加载失败

**症状**: `FileNotFoundError` 或 `ValueError: 配置文件不存在`

**解决方案**:

1. 检查配置文件路径：
```bash
# 项目根目录应该有 config/main.yaml
ls config/main.yaml  # Linux/macOS
dir config\main.yaml  # Windows
```

2. 验证 YAML 语法：
```bash
python -c "import yaml; yaml.safe_load(open('config/main.yaml'))"
```

3. 检查文件编码是否为 UTF-8

---

### IDE 配置文件未找到

**症状**: `IDE 配置文件不存在` 错误

**解决方案**:

1. 检查 `main.yaml` 中的路径配置：
```yaml
ide:
  config_path: config/operations/pycharm.yaml  # 确保此路径正确
```

2. 确保操作配置文件存在：
```bash
ls config/operations/pycharm.yaml
```

3. 如果使用相对路径，确保相对于 `main.yaml` 所在目录

---

### API 密钥未设置

**症状**: `ZHIPUAI_API_KEY not found` 错误

**解决方案**:

**方法 1: 环境变量**
```bash
# Windows (PowerShell)
$env:ZHIPUAI_API_KEY="your_key"

# Windows (CMD)
set ZHIPUAI_API_KEY=your_key

# macOS/Linux
export ZHIPUAI_API_KEY="your_key"
```

**方法 2: .env 文件**
在项目根目录创建 `.env`：
```
ZHIPUAI_API_KEY=your_key_here
```

**方法 3: 直接配置**
编辑 `config/main.yaml`：
```yaml
api:
  zhipuai:
    api_key: "your_key_here"  # 直接填写（不推荐）
```

## API 调用问题

### API 请求超时

**症状**: `Timeout` 或 `请求超时` 错误

**解决方案**:

1. 增加超时时间：
```yaml
api:
  zhipuai:
    timeout: 60  # 增加到 60 秒
```

2. 检查网络连接：
```bash
ping open.bigmodel.cn
```

3. 如果使用代理，确保配置正确：
```bash
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080
```

---

### API 调用失败（401/403）

**症状**: 认证错误或权限不足

**解决方案**:

1. 验证 API 密钥是否正确
2. 检查智谱 AI 账户状态：
   - 登录 [智谱开放平台](https://open.bigmodel.cn/)
   - 检查账户余额
   - 确认 API 密钥状态

3. 重新生成 API 密钥：
   - 在平台上删除旧密钥
   - 创建新密钥
   - 更新本地配置

---

### 返回结果为空

**症状**: AI 返回空结果或无法解析

**解决方案**:

1. 启用调试日志：
```yaml
system:
  log_level: DEBUG
```

2. 查看日志文件：
```bash
cat logs/ui_agent.log | tail -100
```

3. 检查 API 返回的原始内容

4. 如果是 JSON 解析错误，系统会自动尝试修复

## UI 定位问题

### 坐标定位不准确

**症状**: 点击位置偏离目标

**解决方案**:

1. 调整坐标偏移量：
```yaml
automation:
  coordinate_offset: [36, 46]  # [x偏移, y偏移]
```

2. 测试不同偏移值：
   - 如果点击偏左/上，增加偏移
   - 如果点击偏右/下，减少偏移

3. 对于高 DPI 屏幕，可能需要更大偏移：
```yaml
automation:
  coordinate_offset: [72, 92]  # 150% 缩放
```

4. 查看截图以诊断：
```bash
ls screenshots/
```

---

### 无法找到 UI 元素

**症状**: `无法找到目标元素` 或置信度过低

**解决方案**:

1. 确认 PyCharm 窗口在最前面
2. 检查元素是否可见（非折叠状态）
3. 尝试更具体的命令：
   ```
   "双击 main.py" → "双击文件树中的 main.py"
   ```

4. 检查截图目录中的截图，确认捕获了正确的区域

5. 如果使用深色主题，可能需要调整提示词

---

### 视觉识别返回错误

**症状**: `JSON 解析失败` 或 `返回格式错误`

**解决方案**:

1. 系统会自动修复常见的 JSON 格式问题

2. 如果问题持续，检查日志中的原始响应

3. 可能是 API 返回了非预期格式，可以尝试：
   - 简化 visual_prompt
   - 使用更精确的描述

## 自动化执行问题

### 操作无响应

**症状**: 命令执行后没有反应

**解决方案**:

1. 确认 PyCharm 窗口处于活动状态
2. 增加操作超时时间：
```yaml
automation:
  default_timeout: 10.0
```

3. 检查是否有对话框遮挡
4. 尝试手动执行快捷键确认 PyCharm 响应

---

### 操作执行错误

**症状**: 执行了错误的操作

**解决方案**:

1. 检查命令解析是否正确：
```bash
python -m src.main "测试命令" --debug
```

2. 验证参数提取：
```bash
python -m src.main "跳转到第 50 行" --verbose
```

3. 查看操作配置文件确认快捷键正确

4. 使用撤销操作恢复：
```bash
python -m src.main "撤销"
```

---

### 操作序列中断

**症状**: 多步操作只执行了一部分

**解决方案**:

1. 增加重试次数：
```yaml
automation:
  max_retries: 5
  retry_delay: 2.0
```

2. 增加操作间隔：
```yaml
automation:
  action_delay: 0.5
```

3. 检查日志定位失败步骤

## 性能问题

### 命令响应缓慢

**症状**: 执行命令需要超过 5 秒

**解决方案**:

1. 检查网络延迟：
```bash
ping open.bigmodel.cn
```

2. 减少截图区域（如果支持）
3. 启用缓存：
```yaml
# 某些结果会被自动缓存
```

4. 使用更快的模型（牺牲精度）：
```yaml
api:
  zhipuai:
    model: glm-4v-flash  # 快速模型
```

---

### 内存占用过高

**症状**: 程序占用大量内存

**解决方案**:

1. 清空截图历史：
```bash
rm -rf screenshots/*
```

2. 调整日志级别：
```yaml
system:
  log_level: WARNING  # 减少日志输出
```

3. 定期重启程序

## 调试技巧

### 启用详细日志

```yaml
system:
  log_level: DEBUG
```

查看日志：
```bash
tail -f logs/ui_agent.log
```

### 保存调试截图

截图会自动保存在 `screenshots/` 目录，文件名包含时间戳。

### 测试单个模块

```bash
# 测试命令解析
python -m pytest tests/unit/test_command_parser.py -v

# 测试坐标计算
python -m pytest tests/unit/test_coordinates.py -v
```

### 手动验证配置

```python
from src.config.config_manager import ConfigManager

manager = ConfigManager("config/main.yaml")
config = manager.load_config()
print(config)
```

### 诊断脚本

创建诊断脚本 `diagnose.py`：

```python
import os
from pathlib import Path

def diagnose():
    print("=== 环境诊断 ===")

    # 检查 Python 版本
    import sys
    print(f"Python 版本: {sys.version}")

    # 检查 API 密钥
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    print(f"API 密钥: {'已设置' if api_key else '未设置'}")

    # 检查配置文件
    config_files = [
        "config/main.yaml",
        "config/operations/pycharm.yaml"
    ]
    for f in config_files:
        exists = Path(f).exists()
        print(f"{f}: {'存在' if exists else '不存在'}")

    # 检查目录
    dirs = ["logs", "screenshots"]
    for d in dirs:
        exists = Path(d).exists()
        print(f"{d}/: {'存在' if exists else '不存在'}")

if __name__ == "__main__":
    diagnose()
```

## 获取帮助

如果问题仍未解决：

1. 查看 [架构文档](ARCHITECTURE.md) 了解系统内部工作原理
2. 检查 GitHub Issues 是否有类似问题
3. 创建新的 Issue，包含：
   - 错误信息
   - 配置文件内容
   - 日志文件片段
   - 系统环境信息
