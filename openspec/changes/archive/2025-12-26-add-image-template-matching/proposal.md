# 提案：支持根据子图片识别在完整图片中的位置并点击

## 变更ID

`add-image-template-matching`

## 概述

添加基于模板匹配的 UI 元素定位能力，允许用户提供子图片（模板图片），系统在完整屏幕截图中查找该子图片的位置，并执行点击等操作。

## 动机

当前项目的 UI 元素定位主要依赖两种方式：

1. **大模型视觉识别** (GLM-4V)：通过自然语言描述定位 UI 元素
   - 成本高：每次调用产生 API 费用
   - 网络依赖：需要稳定的网络连接
   - 延迟：API 调用有网络延迟

2. **OCR 文本识别**：通过识别屏幕上的文本来定位
   - 局限性：仅适用于有文本的元素
   - 依赖：需要安装 EasyOCR 或 Tesseract

**模板匹配的优势**：

1. **无需网络**：完全本地处理，无网络依赖
2. **零成本**：不调用任何 API
3. **高精度**：对于固定的 UI 元素（图标、按钮、logo 等）识别准确
4. **快速**：本地算法处理速度快
5. **简单直观**：用户只需截取目标元素的图片作为模板

## 影响范围

### 修改范围

1. **新增模板匹配定位器**
   - 创建 `src/locator/template_matcher.py`
   - 使用 OpenCV 的模板匹配算法

2. **配置系统**
   - 在 `config/main.yaml` 中添加模板图片目录配置
   - 支持模板图片管理（添加、删除、更新）
   - **目录设计**：模板图片存储在项目根目录的 `templates/` 目录下，与源码（`src/`）解耦

3. **命令解析**
   - 添加新的意图类型或扩展现有解析器
   - 支持通过模板名称引用子图片

4. **操作配置**
   - 在 `pycharm.yaml` 中添加基于模板匹配的操作示例

### 目录结构

```
UI-Agent/
├── src/                    # 源码目录
│   └── locator/
│       └── template_matcher.py
├── templates/              # 模板图片目录（与 src 解耦）
│   ├── run_button.png
│   ├── save_icon.png
│   └── ...
├── config/
│   └── main.yaml
└── ...
```

### 非影响范围

- 现有的视觉识别和 OCR 定位方式保持不变
- 自动化执行模块不受影响

## 替代方案

### 方案 A：纯 PIL 实现
使用 Pillow 库的图像比较功能。

**优点**：无需额外依赖
**缺点**：功能有限，不支持缩放、旋转等复杂场景

### 方案 B：OpenCV 模板匹配（推荐）
使用 OpenCV 的 `matchTemplate` 函数。

**优点**：
- 成熟可靠的算法
- 支持多种匹配方法
- 性能优秀
- 可处理不同尺度的模板

**缺点**：需要添加 OpenCV 依赖

### 方案 C：纯视觉模型扩展
改进现有视觉模型，支持图片输入。

**优点**：统一接口
**缺点**：仍然依赖 API 和网络，违背了本地化的初衷

## 风险评估

- **依赖风险**：低 - OpenCV 是成熟的库，Python 支持良好
- **功能风险**：中 - 模板匹配对 UI 缩放、主题变化敏感
- **测试风险**：中 - 需要准备各种模板图片进行测试

## 依赖项

- 新增依赖：`opencv-python` 或 `opencv-python-headless`

### 依赖说明

```toml
dependencies = [
    # ... 现有依赖
    "opencv-python>=4.8.0",  # 或 opencv-python-headless 用于无 GUI 环境
]
```

## 向后兼容性

完全向后兼容。新功能是可选的，不影响现有使用方式。

## 使用示例

### 配置文件

**主配置文件 (`config/main.yaml`)**

```yaml
# 添加模板匹配配置段
template_matching:
  # 模板图片存储目录（相对于项目根目录）
  template_dir: templates/
  # 默认匹配置信度阈值 (0.0-1.0)
  default_confidence: 0.8
  # 匹配方法: TM_CCOEFF_NORMED（推荐）、TM_CCORR_NORMED、TM_SQDIFF
  method: TM_CCOEFF_NORMED
  # 是否支持多尺度匹配（应对不同 DPI/缩放）
  enable_multiscale: false
```

**操作配置文件 (`config/operations/pycharm.yaml`)**

```yaml
- name: click_run_button
  aliases: [点击运行, run]
  intent: template_match
  description: 点击运行按钮（使用模板匹配）

  template: run_button.png  # 模板图片文件名（相对于 template_dir）
  confidence: 0.8  # 匹配置信度阈值（可选，默认使用配置文件中的值）

  actions:
    - type: click
      target: "0"
```

### 命令格式

```bash
# 通过配置文件中的操作名执行
python -m src.main "点击运行按钮"

# 直接指定模板文件（相对于 template_dir）
python -m src.main "点击按钮" --template database-button.png
```


## 参考资料

- OpenCV 模板匹配：https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
- 现有定位器实现：`src/locator/visual_locator.py`
- 现有规范：
  - `vision-config`: 视觉识别配置
  - `input-field-action`: 输入框操作
