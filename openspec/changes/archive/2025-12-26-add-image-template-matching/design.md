# 设计文档：图片模板匹配定位器

## 架构概述

### 组件关系

```
┌─────────────────────────────────────────────────────────────┐
│                      IDEController                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              CommandParser                              ││
│  │  - 解析命令                                              ││
│  │  - 提取模板名称（如果有）                                 ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              LocatorRouter (新增)                        ││
│  │  - 根据配置选择定位方式：                                  ││
│  │    1. 模板匹配（如果指定了模板）                           ││
│  │    2. 视觉识别（如果启用）                                 ││
│  │    3. OCR（回退方案）                                     ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         ▼                 ▼                 ▼               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Template │      │  Vision  │      │   OCR    │          │
│  │  Matcher │      │  Locator │      │ Locator  │          │
│  └──────────┘      └──────────┘      └──────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. TemplateMatcher 类

**职责**：使用 OpenCV 进行模板匹配

**主要方法**：

```python
class TemplateMatcher:
    def __init__(self, template_dir: str):
        """初始化，指定模板图片存储目录"""

    def load_template(self, template_name: str) -> np.ndarray:
        """加载模板图片"""

    def match(
        self,
        screenshot: Image.Image,
        template_name: str,
        threshold: float = 0.8
    ) -> list[UIElement]:
        """在截图中匹配模板

        Args:
            screenshot: 屏幕截图
            template_name: 模板图片名称
            threshold: 匹配阈值（0-1）

        Returns:
            匹配到的 UI 元素列表（可能有多个匹配）
        """

    def match_all_sizes(
        self,
        screenshot: Image.Image,
        template_name: str,
        threshold: float = 0.8,
        scales: list[float] = None
    ) -> list[UIElement]:
        """支持多尺度匹配（处理 UI 缩放）"""
```

### 2. 模板图片管理

**存储结构**：

```
config/
├── main.yaml
├── operations/
│   └── pycharm.yaml
└── templates/              # 新增目录
    ├── run_button.png
    ├── save_icon.png
    ├── debug_button.png
    └── ...
```

**配置方式**：

```yaml
# config/main.yaml
templates:
  dir: config/templates/  # 模板图片目录
  cache_enabled: true     # 是否缓存加载的模板
```

### 3. 匹配算法选择

OpenCV 提供多种模板匹配方法：

| 方法 | 常量 | 特点 |
|------|------|------|
| 平方差匹配 | TM_SQDIFF | 值越小匹配越好 |
| 标准化平方差 | TM_SQDIFF_NORMED | 归一化，范围 [0, 1] |
| 相关匹配 | TM_CCORR | 值越大匹配越好 |
| 标准化相关匹配 | TM_CCORR_NORMED | 归一化 |
| 相关系数匹配 | TM_CCOEFF | 值越大匹配越好 |
| 标准化相关系数 | TM_CCOEFF_NORMED | **推荐**，最准确 |

**推荐方案**：使用 `TM_CCOEFF_NORMED`，因为它：
- 归一化结果，范围 [-1, 1]
- 对光照变化不敏感
- 1 表示完美匹配

### 4. 多尺度匹配

为了处理 UI 缩放（高 DPI、不同分辨率），实现多尺度匹配：

```python
def match_all_sizes(self, screenshot, template, threshold, scales):
    results = []
    for scale in scales:
        # 缩放模板
        scaled_template = cv2.resize(template, None, fx=scale, fy=scale)

        # 执行匹配
        matches = self._match_single_scale(screenshot, scaled_template)

        # 过滤低置信度结果
        results.extend([m for m in matches if m.confidence >= threshold])

    # 按置信度排序，返回最佳匹配
    return sorted(results, key=lambda x: x.confidence, reverse=True)
```

### 5. 与现有系统集成

#### 5.1 定位器路由

在 `IDEController` 中添加定位器选择逻辑：

```python
def locate_element(
    self,
    prompt: str,
    template_name: str = None,
    target_filter: str = None
) -> list[UIElement]:
    """路由到适当的定位器"""

    # 优先级 1: 模板匹配（如果指定）
    if template_name:
        return self.template_matcher.match(screenshot, template_name)

    # 优先级 2: 视觉识别（如果启用）
    if self.config.vision.enabled:
        return self.vision_locator.locate(prompt, screenshot, target_filter)

    # 优先级 3: OCR 回退
    return self.vision_locator._locate_with_ocr(screenshot, target_filter)
```

#### 5.2 命令解析扩展

```python
class CommandParser:
    def parse(self, command: str) -> ParsedCommand:
        """解析命令，提取模板名称（如果有）"""

        # 检查是否包含模板引用
        # 例如："点击运行按钮[run_button.png]"
        # 或通过命令行参数 --template 指定
```

## 性能考虑

### 优化策略

1. **模板缓存**：加载后的模板图片缓存在内存中
2. **感兴趣区域（ROI）**：支持在指定区域内搜索，减少计算量
3. **降采样**：对大图先缩小再匹配，提高速度
4. **早期退出**：找到高置信度匹配后可提前返回

### 性能基准

| 操作 | 预期耗时 |
|------|----------|
| 加载模板（首次） | ~10ms |
| 单尺度匹配 (1920x1080) | ~20-50ms |
| 多尺度匹配 (5个尺度) | ~100-250ms |

## 边界情况处理

### 1. 模板未找到

```python
try:
    template = self.load_template(name)
except FileNotFoundError:
    logger.error(f"模板图片不存在: {name}")
    return []
```

### 2. 无匹配结果

```python
matches = self.match(screenshot, template)
if not matches:
    logger.warning(f"未找到匹配的模板: {template}")
    return []
```

### 3. 多个匹配结果

```python
# 按置信度排序
matches.sort(key=lambda x: x.confidence, reverse=True)

# 返回所有超过阈值的匹配
return [m for m in matches if m.confidence >= threshold]
```

## 配置示例

### 完整配置

```yaml
# config/main.yaml
templates:
  dir: config/templates/
  cache_enabled: true
  default_threshold: 0.8
  default_scales: [0.8, 0.9, 1.0, 1.1, 1.2]

# config/operations/pycharm.yaml
- name: click_run_button
  aliases: [点击运行, run]
  intent: template_match
  description: 点击运行按钮

  template: run_button.png
  threshold: 0.85
  max_matches: 1

  actions:
    - type: click
      target: "0"
```

## 测试策略

### 单元测试

1. **模板加载测试**：验证能正确加载模板图片
2. **匹配准确性测试**：使用已知图片对验证匹配结果
3. **阈值测试**：验证不同阈值下的匹配行为

### 集成测试

1. **端到端测试**：从命令解析到点击执行
2. **多场景测试**：不同 UI、不同分辨率

### 测试数据

```
tests/fixtures/
├── templates/
│   ├── button_template.png
│   └── icon_template.png
└── screenshots/
    ├── screen_with_button.png
    └── screen_with_icon.png
```
