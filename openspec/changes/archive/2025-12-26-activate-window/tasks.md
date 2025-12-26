# 任务列表

## 阶段 1：核心功能实现

### 1.1 创建窗口管理模块
- [x] 创建 `src/window/` 目录结构
- [x] 创建 `src/window/exceptions.py` 模块（异常类定义）
- [x] 创建 `src/window/window_manager.py` 模块
- [x] 实现 `WindowManager` 类
- [x] 实现 `find_window(title: str)` 方法：根据标题查找窗口
- [x] 实现 `find_by_process_name(process_name: str)` 方法：根据进程名查找窗口
- [x] 实现 `activate_window(title: str)` 方法：激活指定窗口
- [x] 实现 `activate_by_process(process_name: str)` 方法：通过进程名激活窗口
- [x] 实现 `restore_window()` 方法：恢复最小化窗口
- [x] 实现 `list_windows()` 方法：列出所有窗口标题
- [x] 实现 `list_processes()` 方法：列出所有运行的进程
- [x] 添加错误处理和日志记录
- [x] 添加 Windows 平台增强功能（Win32 API 强制激活）

### 1.2 添加依赖项
- [x] 将 `pygetwindow` 添加到 `pyproject.toml` 依赖列表
- [x] 添加 `pywin32` 可选依赖（Windows 增强）
- [x] 添加 `psutil` 可选依赖（进程查找）
- [x] 验证 uv.lock 中已有相关依赖

### 1.3 集成到 IDE 控制器
- [x] 在 `IDEController` 中添加 `_window_manager` 成员
- [x] 在 `IDEController.__init__()` 中初始化 `WindowManager`
- [x] 添加 `activate_window(window_title: str)` 公共方法
- [x] 添加 `activate_pycharm()` 便捷方法

### 1.4 配置窗口激活操作
- [x] 在 `config/operations/pycharm.yaml` 中添加 `activate_window` 操作
- [x] 定义操作别名：激活窗口、切换到 PyCharm、activate window
- [x] 配置默认窗口标题匹配模式

## 阶段 2：测试与验证

### 2.1 单元测试
- [x] 创建 `tests/unit/test_window_manager.py`
- [x] 测试窗口查找功能（使用 mock）
- [x] 测试窗口激活功能（使用 mock）
- [x] 测试窗口未找到场景
- [x] 测试最小化窗口恢复场景
- [x] 测试进程查找功能（使用 mock）
- [x] 测试异常处理和错误信息

### 2.2 集成测试
- [ ] 创建 `tests/integration/test_window_activation_integration.py`
- [ ] 测试完整的激活窗口流程
- [ ] 测试与 IDE 控制器的集成
- [ ] 测试进程名激活功能

### 2.3 手动验证
- [ ] 在实际 PyCharm 环境中测试激活功能
- [ ] 测试最小化窗口的激活
- [ ] 测试窗口不存在时的错误处理
- [ ] 测试以管理员权限运行的应用激活

## 阶段 3：文档与完善

### 3.1 更新文档
- [x] 在 README.md 中添加窗口激活功能说明
- [x] 在 COMMANDS.md 中添加激活窗口命令示例
- [x] 更新 INSTALL.md 中的依赖说明
- [x] 添加权限问题的解决方案说明

### 3.2 代码质量
- [x] 运行 black 格式化代码
- [x] 运行 ruff 检查代码
- [x] 运行 mypy 类型检查
- [x] 确保测试覆盖率（单元测试覆盖核心功能，Windows API 部分需集成测试）

**测试覆盖率说明**：
- `window_manager.py`: 49% - 核心功能已覆盖
- `exceptions.py`: 92%
- 单元测试：25 个通过，3 个跳过（需要实际 Windows 环境）
- 未覆盖部分主要是 Windows 特定的 Win32 API 和 psutil 调用，需要在集成测试中验证

## 阶段 4：后续优化

### 4.1 功能增强
- [ ] 支持正则表达式窗口匹配
- [ ] 添加窗口历史记录功能
- [ ] 支持多显示器环境下的窗口激活

### 4.2 跨平台支持
- [ ] macOS 平台窗口管理实现
- [ ] Linux 平台窗口管理实现

## 任务依赖关系

```
1.1 ───> 1.2 ───> 1.3 ───> 1.4
                │
                └──> 2.1 ───> 2.2 ───> 2.3
                                          │
                                          └──> 3.1 ───> 3.2
                                                    │
                                                    └──> 4.1 ───> 4.2
```

## 可并行任务

- 2.1（单元测试）可与 1.4（配置操作）并行开发
- 3.1（文档）可与 2.3（手动验证）并行进行
- 4.1（功能增强）可与 4.2（跨平台支持）并行开发

## 验收检查点

每个阶段完成后应满足：
1. **阶段 1**：代码编译通过，基本功能可用 ✅
2. **阶段 2**：所有测试通过，功能验证完毕（单元测试完成 ✅）
3. **阶段 3**：文档完整，代码质量检查通过 ✅
4. **阶段 4**：跨平台支持，功能增强

---

## 实现说明

### 修复的问题

**问题**：命令 "切换到Edge浏览器" 无法激活窗口

**原因**：
- 提取的窗口标题是 "Edge浏览器"，但进程名映射表中只有 "Edge" 和 "edge"
- 实际 Edge 浏览器的进程名是 `msedge.exe`

**解决方案**：
1. 添加后缀词清理逻辑：自动去除 "浏览器"、"窗口"、"软件"、"程序"、"应用" 等常见后缀
2. 扩展应用名映射表：添加更多中文变体（如 "谷歌"、"火狐"、"微软" 等

**修改的代码**：
- `src/controller/ide_controller.py`:
  - 第 155-160 行：添加后缀词清理逻辑
  - 第 608-632 行：扩展应用名映射表

### 已实现的功能特性

1. **窗口查找**：
   - 支持通过窗口标题查找（精确和模糊匹配）
   - 支持通过进程名查找（需要 psutil）
   - 自动过滤无标题或不可见的窗口

2. **窗口激活**：
   - 标准激活方法（pygetwindow）
   - Windows 增强激活（Win32 API）
   - 自动处理最小化窗口
   - 权限问题的友好提示

3. **错误处理**：
   - `WindowNotFoundError`：窗口未找到时抛出，附带可用窗口列表
   - `WindowActivationError`：激活失败时抛出，包含详细错误信息
   - 权限问题的特殊处理和解决方案提示

4. **辅助功能**：
   - `list_windows()`：列出所有窗口标题
   - `list_processes()`：列出所有运行的进程
   - `is_window_minimized()`：检查窗口是否最小化

### 已知限制

1. **平台支持**：当前主要支持 Windows 平台
2. **权限问题**：激活以管理员权限运行的应用需要提升权限
3. **窗口匹配**：部分匹配可能匹配到多个窗口，选择第一个

### 待解决问题

1. 需要添加集成测试验证完整功能
2. 需要在实际环境中测试各种 IDE 的窗口激活

