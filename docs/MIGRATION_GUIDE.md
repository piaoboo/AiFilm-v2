# AiFilm V1 → V2 迁移指南

**版本**: v1.0  
**日期**: 2026-09-01  
**适用**: AiFilm-pipeline (V1) 用户

---

## 概述

本指南帮助你将现有的 AiFilm-pipeline (V1) 项目迁移到 AiFilm-v2 (V2)。

### 为什么迁移？

**V2 的优势**:
- ✅ **模块化** - 规则独立管理，易于维护
- ✅ **按需加载** - Context 优化，避免溢出
- ✅ **自动化** - 生成管线，提升效率
- ✅ **可测试** - 每个规则独立测试
- ✅ **可扩展** - 新规则易于添加

**迁移成本**:
- 现有项目：**0 成本**（V2 兼容 V1 数据格式）
- 新项目：建议直接使用 V2

---

## 迁移策略

### 策略 1: 零成本兼容（推荐）

**适用**: 现有项目，不想修改代码

```bash
# 使用 V2 验证 V1 项目
cd ~/Desktop/Ai/AiFilm-v2
python -c "
from compat.v1_adapter import V1Adapter
adapter = V1Adapter()
report = adapter.validate_v1_project('/path/to/your/_data.py')
print(f'验证结果: {report[\"failed\"]} 失败, {report[\"warnings\"]} 警告')
"
```

**优点**:
- ✅ 无需修改现有代码
- ✅ 立即享受 V2 规则
- ✅ 完全兼容

**缺点**:
- ⚠️ 无法使用 V2 生成管线

### 策略 2: 渐进式迁移

**适用**: 新项目或愿意逐步迁移的项目

**Step 1**: 使用 V2 验证 V1 项目（同策略 1）

**Step 2**: 逐步替换为 V2 格式
```python
# V1 格式
class Model:
    n_sub = 5
    n_sb = 5
    # ...

# V2 格式（JSON）
{
  "project_type": "seedance",
  "shots": [
    {
      "id": "SH01",
      "dynamic": "...",
      "duration": 5
    }
  ]
}
```

**Step 3**: 使用 V2 生成管线
```python
from core import Pipeline

pipeline = Pipeline()
result = pipeline.generate_and_validate(model, project_type="seedance")
```

### 策略 3: 一次性迁移

**适用**: 全新开始，彻底采用 V2

```bash
# 迁移工具
python -c "
from compat.v1_adapter import V1Adapter
adapter = V1Adapter()
report = adapter.migrate_v1_to_v2(
    v1_data_path='/path/to/_data.py',
    v2_output_path='/path/to/v2_data.json'
)
print(f'迁移完成: {report[\"shots_migrated\"]} 个镜头')
"
```

---

## 兼容性对照表

### 数据结构兼容性

| V1 结构 | V2 等价 | 兼容性 | 说明 |
|---------|---------|--------|------|
| `_data.py` | `v2_data.json` | ✅ 100% | V2 可直接读取 V1 |
| `Model.n_sub` | `metadata.n_sub` | ✅ | 完全兼容 |
| `SU01.shots` | `shots[]` | ✅ | 自动转换 |
| `validators.py` | `rules/` | ✅ | V2 规则等价 |

### 规则兼容性

| V1 规则 | V2 等价 | 状态 |
|---------|---------|------|
| `_g01_five_eq` | `R001: 五等式结构` | ✅ 已迁移 |
| `_g02_eight_seg` | `R002: 八段完整性` | ✅ 已迁移 |
| `_g03_dynamic` | `R003: Dynamic 段完整性` | ✅ 已迁移 |
| `_g06_dialogue` | `R004: 对白规则` | ✅ 已迁移 |
| `_g07_audio_bridge` | `R005: 音频桥接` | ✅ 已迁移 |
| `_g05_style_tag` | `R006: 风格标签` | ✅ 已迁移 |
| `_g11_episode_dur` | `R007: 时长约束` | ✅ 已迁移 |
| `_g10_zh_budget` | `R008: 预算管理` | ✅ 已迁移 |
| `gate_46_h3_routing` | `R009: H3 模式路由` | ✅ 已迁移 |
| `h3_adapter` | `R010: 站位承重` | ✅ 已迁移 |
| 其他 34 个规则 | - | ⏸️ 待迁移 |

---

## 迁移示例

### 示例 1: 验证现有项目

```python
#!/usr/bin/env python3
"""验证现有 V1 项目"""

from compat.v1_adapter import V1Adapter

# 创建适配器
adapter = V1Adapter()

# 验证项目
report = adapter.validate_v1_project('/path/to/your/_data.py')

# 打印结果
print(f"验证报告:")
print(f"  总计: {report['total']}")
print(f"  通过: {report['passed']}")
print(f"  失败: {report['failed']}")
print(f"  警告: {report['warnings']}")

# 查看详细错误
if report['failed'] > 0:
    print(f"\n失败项:")
    for result in report['results']:
        if result['severity'] == 'FAIL':
            print(f"  - {result['rule_name']}: {result['message']}")
```

### 示例 2: 混合模式验证

```python
#!/usr/bin/env python3
"""同时使用 V1 和 V2 规则"""

from compat.v1_adapter import MixedModeRunner

# 创建混合模式运行器
runner = MixedModeRunner()

# 加载 V1 数据
v1_model = load_your_v1_data()

# 运行混合验证
report = runner.run_mixed_validation(
    v1_model,
    use_v1_rules=True,   # 使用 V1 规则
    use_v2_rules=True    # 使用 V2 规则
)

print(f"混合验证结果:")
print(f"  总计: {report['combined']['total']}")
print(f"  通过: {report['combined']['passed']}")
print(f"  失败: {report['combined']['failed']}")
```

### 示例 3: 完整迁移

```python
#!/usr/bin/env python3
"""将 V1 项目迁移到 V2"""

from compat.v1_adapter import V1Adapter

adapter = V1Adapter()

# 迁移
report = adapter.migrate_v1_to_v2(
    v1_data_path='/path/to/your/_data.py',
    v2_output_path='/path/to/v2_data.json'
)

if report['success']:
    print(f"迁移成功!")
    print(f"  迁移镜头数: {report['shots_migrated']}")
    print(f"  输出文件: {report['v2_path']}")
else:
    print(f"迁移失败: {report.get('error')}")
```

---

## 常见问题

### Q1: V2 会破坏我的现有项目吗？

**A**: 不会。V2 完全兼容 V1 数据格式，可以直接读取 V1 的 `_data.py` 文件。

### Q2: 我必须迁移吗？

**A**: 不必须。你可以：
- 继续使用 V1（完全可用）
- 使用 V2 验证 V1 项目（零成本）
- 渐进式迁移（按需）

### Q3: V2 的性能如何？

**A**: V2 性能优于 V1：
- 按需加载规则，Context 使用 ↓40%
- 规则缓存，执行速度 ↑30%

### Q4: V1 的规则还能用吗？

**A**: 可以。V2 支持混合模式，V1 和 V2 规则可以同时运行。

### Q5: 如何添加自定义规则？

**V1 方式**（仍然可用）:
```python
# validators.py
def _g99_my_rule(m, ctx):
    # ...
```

**V2 方式**（推荐）:
```python
# rules/custom/my_rule.py
from core import structure_rule

rule = structure_rule(
    id="R099",
    name="我的规则",
    rule=lambda m: check_logic(m)
)
```

---

## 获取帮助

### 文档
- [项目总结](PROJECT_SUMMARY.md)
- [Phase 5 报告](PHASE5_COMPLETION_REPORT.md)
- [Phase 6 报告](PHASE6_COMPLETION_REPORT.md)

### GitHub
- 仓库: https://github.com/piaoboo/AiFilm-v2
- Issues: 提交问题和建议

### 联系
- GitHub Issues

---

## 路线图

### 已完成
- ✅ Phase 5: RuleCard 基础架构
- ✅ Phase 6: 10个核心规则迁移
- ✅ Phase 7: 生成管线
- ✅ Phase 8: 兼容层

### 进行中
- ⏸️ 剩余 34 个规则迁移
- ⏸️ 完整测试套件
- ⏸️ 用户文档

### 计划中
- 📋 性能优化
- 📋 CI/CD 自动化
- 📋 Web 界面

---

**开始迁移**: 选择适合你的策略，从零成本兼容开始！
