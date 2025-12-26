# 任务列表：支持通过配置关闭基于大模型的视觉识别

## 任务概述

本变更将添加配置选项，允许用户禁用基于大模型的视觉识别功能。

---

## 任务 1：扩展配置架构

- [x] 在 `schema.py` 中新增 `VisionConfig` 数据类
- [x] 更新 `MainConfig` 数据类，添加 `vision: VisionConfig` 字段
- [x] 更新 `config_manager.py` 中的 `_parse_main_config` 方法，解析视觉配置
- [x] 在 `config/main.yaml` 中添加 `vision` 配置示例

**状态**: 已完成

---

## 任务 2：修改 VisualLocator 支持配置控制

- [x] 修改 `__init__` 方法，添加 `vision_enabled: bool = True` 参数
- [x] 将该参数存储为实例变量 `self._vision_enabled`
- [x] 修改 `locate` 方法，当 `vision_enabled=False` 时跳过大模型识别
- [x] 添加日志输出，说明当前使用的定位方式

**状态**: 已完成

---

## 任务 3：修改 IDEController 传递配置

- [x] 在创建 `VisualLocator` 实例时，传入 `vision_enabled` 参数
- [x] 从 `self.config.vision.enabled` 读取配置

**状态**: 已完成

---

## 任务 4：更新单元测试

- [x] 测试配置加载：验证 `vision.enabled` 配置项能够正确解析
- [x] 测试 `VisionConfig` 默认值和禁用状态
- [x] 验证所有测试通过

**状态**: 已完成

---

## 任务 5：更新文档

- [x] 在配置文件中添加详细注释，说明 `vision.enabled` 的作用
- [x] 在 `docs/USAGE.md` 中添加配置说明
- [x] 说明禁用后的行为和限制

**状态**: 已完成

---

## 实施总结

所有任务已完成。主要修改：

1. **配置系统** (`src/config/schema.py`, `src/config/config_manager.py`)
   - 新增 `VisionConfig` 数据类
   - 更新 `MainConfig` 包含 `vision` 字段

2. **定位器** (`src/locator/visual_locator.py`)
   - 添加 `vision_enabled` 参数
   - 在 `locate` 方法中根据配置决定定位策略

3. **控制器** (`src/controller/ide_controller.py`)
   - 传递视觉识别配置给定位器

4. **测试** (`tests/unit/test_config.py`)
   - 添加 `VisionConfig` 相关测试

5. **文档** (`config/main.yaml`, `docs/USAGE.md`)
   - 添加配置说明和使用指南

**测试结果**: 所有测试通过 (14 passed, 3 skipped)
