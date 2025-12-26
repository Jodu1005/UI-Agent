# 任务列表

## 阶段1：核心功能实现

### 1.1 添加 INPUT 意图类型
**文件**: `src/parser/intents.py`
- [x] 在 `IntentType` 枚举中添加 `INPUT` 类型
- [x] 在 `INTENT_KEYWORDS` 中添加相关关键词映射

**验收**: 代码编译通过，新意图类型可访问

---

### 1.2 扩展命令解析器
**文件**: `src/parser/command_parser.py`
- [x] 在 `_extract_parameters` 方法中添加输入框相关参数提取：
  - `context_text`: 上下文描述（如"本地"）
  - `position_hint`: 位置提示（如"下方"）
  - `input_text`: 要输入的文本
- [x] 支持解析命令格式：
  - "在{context_text}{position_hint}的输入框中输入{input_text}并回车"
  - "在{context_text}{position_hint}输入{input_text}"

**验收**: 能正确解析示例命令并提取参数

---

### 1.3 添加 input_text 操作配置
**文件**: `config/operations/pycharm.yaml`
- [x] 添加 `input_text` 操作配置：
  - aliases: [输入, 输入文本, 在输入框中输入]
  - intent: input
  - visual_prompt: 支持上下文描述定位
  - actions: click → type → enter 序列

**验收**: 配置文件格式正确，操作可被加载

---

## 阶段2：测试验证

### 2.1 单元测试 - 意图识别
**文件**: `tests/parser/test_intents.py` (新建)
- [x] 测试 INPUT 意图能被正确识别
- [x] 测试关键词匹配

**验收**: 测试通过

---

### 2.2 单元测试 - 命令解析
**文件**: `tests/parser/test_command_parser.py` (新建)
- [x] 测试参数提取：context_text, position_hint, input_text
- [x] 测试各种命令格式变体

**验收**: 测试通过，参数提取正确

---

### 2.3 集成测试
**文件**: `tests/integration/test_input_field.py` (新建)
- [ ] 端到端测试：从命令解析到执行验证
- [ ] 使用模拟截图和定位器

**验收**: 集成测试通过（暂未实现）

---

## 阶段3：文档与优化

### 3.1 更新 README
**文件**: `README.md`
- [x] 在"支持的命令"部分添加输入框操作示例

**验收**: 文档更新完整

---

### 3.2 优化视觉提示词
**文件**: `config/operations/pycharm.yaml`
- [x] 根据测试结果优化 visual_prompt
- [x] 改进上下文描述的定位准确度

**验收**: 定位成功率提升

---

## 任务依赖关系

```
1.1 添加 INPUT 意图类型
  ↓
1.2 扩展命令解析器 ─────┐
  ↓                      │
1.3 添加 input_text配置  │
  ↓                      │
2.1 意图识别测试 ←───────┘
  ↓
2.2 命令解析测试
  ↓
3.1 更新 README ─── 3.2 优化提示词
```

## 可并行任务

- `2.1` 和 `1.3` 可以并行开发
- `3.1` 和 `3.2` 可以并行进行

## 验证清单

- [x] 所有单元测试通过
- [ ] 集成测试通过（暂未实现）
- [ ] 手动验证示例命令执行成功
- [x] 文档更新完整
- [x] 代码通过测试检查
