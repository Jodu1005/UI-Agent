# vision-config Specification

## Purpose
TBD - created by archiving change disable-vision-recognition. Update Purpose after archive.
## 需求
### 需求：视觉识别配置开关

系统**必须**支持通过配置文件控制视觉识别功能的启用状态。

#### 场景：默认启用视觉识别

**给定**：配置文件中未指定 `vision.enabled` 或设置为 `true`

**当**：系统启动并执行 UI 定位操作

**那么**：
- 系统应使用大模型视觉识别作为主要定位方式
- 行为与当前实现保持一致

#### 场景：禁用视觉识别

**给定**：配置文件中设置 `vision.enabled: false`

**当**：系统执行 UI 定位操作

**那么**：
- 系统不应调用大模型视觉 API
- 系统应使用 OCR 定位方式
- 日志应输出"视觉识别已禁用，使用 OCR 定位"

#### 场景：配置热更新

**给定**：系统正在运行且启用了热更新
**并且**：初始配置 `vision.enabled: true`

**当**：配置文件被修改为 `vision.enabled: false`

**那么**：
- 下次定位操作应使用 OCR 而非大模型
- 无需重启系统

---

### 需求：配置数据模型

配置系统**必须**支持视觉识别相关的配置项。

#### 场景：配置解析

**给定**：配置文件包含以下内容：

```yaml
vision:
  enabled: false
```

**当**：配置管理器加载配置

**那么**：
- `MainConfig.vision.enabled` 应为 `false`
- 配置验证应通过

#### 场景：默认值

**给定**：配置文件不包含 `vision` 部分

**当**：配置管理器加载配置

**那么**：
- `MainConfig.vision.enabled` 应默认为 `true`

---

### 需求：定位器行为控制

`VisualLocator` **必须**根据配置决定定位策略。

#### 场景：启用状态下的定位

**给定**：`VisualLocator` 初始化时 `vision_enabled=true`
**并且**：调用 `locate(prompt, screenshot, target_filter="example")`

**当**：执行定位操作

**那么**：
- 首先尝试使用大模型视觉识别（`_locate_with_vision`）
- 如果有 `target_filter` 且支持 OCR，使用混合定位（`_locate_hybrid`）
- 行为与当前实现一致

#### 场景：禁用状态下的定位

**给定**：`VisualLocator` 初始化时 `vision_enabled=false`
**并且**：调用 `locate(prompt, screenshot, target_filter="example")`

**当**：执行定位操作

**那么**：
- 不应调用 `client.chat.completions.create`（大模型 API）
- 应直接使用 OCR 定位（`_locate_with_ocr`）
- 如果 OCR 不可用，返回空列表

---

