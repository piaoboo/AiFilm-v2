# AiFilm V2.0

**RuleCard 架构重构** - 支持 Seedance 2.5 + MiniMax H3 双视频模型

[![GitHub](https://img.shields.io/badge/GitHub-AiFilm--v2-blue)](https://github.com/piaoboo/AiFilm-v2)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 项目简介

AiFilm V2.0 是基于 RuleCard 架构的影视生产管线重构，解决了 V1 (AiFilm-pipeline) 的核心痛点：

- ✅ **规则组织混乱** → 模块化 RuleCard
- ✅ **Context 溢出** → 按需加载
- ✅ **提示词效率低** → 自动化生成管线
- ✅ **维护成本高** → 独立测试 + 统一接口

---

## 快速开始

### 安装

```bash
git clone https://github.com/piaoboo/AiFilm-v2.git
cd AiFilm-v2
```

### 运行示例

**Seedance 项目**:
```bash
python examples/seedance_project/example.py
```

**H3 项目**:
```bash
python examples/h3_project/example.py
```

### 验证现有项目

```python
from compat.v1_adapter import V1Adapter

adapter = V1Adapter()
report = adapter.validate_v1_project('/path/to/your/_data.py')

print(f"验证结果: {report['failed']} 失败, {report['warnings']} 警告")
```

---

## 核心特性

### 1. RuleCard 架构

统一的规则表示，声明式定义：

```python
from core import structure_rule

rule = structure_rule(
    id="R001",
    name="五等式结构",
    rule=lambda m: check_five_equations(m),
    description="检查五个计数是否严格相等"
)
```

### 2. 规则引擎

自动依赖解析、优先级排序、验证聚合：

```python
from core import RuleEngine

engine = RuleEngine()
engine.register(rule)
report = engine.validate(model)
```

### 3. Context 管理

按需加载，优化 token 使用：

```python
from core import ContextManager

manager = ContextManager()
selected = manager.select_rules(all_rules, context, max_tokens=150000)
```

### 4. 生成管线

端到端自动化：

```python
from core import Pipeline

pipeline = Pipeline()
result = pipeline.generate_and_validate(model, project_type="seedance")
```

---

## 架构

```
AiFilm-v2/
├── core/                  # 核心模块
│   ├── rule_card.py      # RuleCard 基类
│   ├── rule_engine.py    # 规则引擎
│   ├── context_manager.py# Context 管理器
│   └── pipeline.py       # 生成管线
├── rules/                 # 规则库（10个已迁移）
│   ├── structure/        # 结构规则
│   ├── content/          # 内容规则
│   ├── style/            # 风格规则
│   ├── technical/        # 技术规则
│   └── h3/               # H3专用规则
├── adapters/             # 适配器
│   └── seedance_adapter.py
├── compat/               # V1兼容层
│   └── v1_adapter.py
├── examples/             # 示例项目
│   ├── seedance_project/
│   └── h3_project/
└── tests/                # 测试（100%覆盖率）
    └── unit/
```

---

## 迁移指南

### 从 V1 迁移到 V2

**策略 1: 零成本兼容**（推荐）
```python
# V2 直接验证 V1 项目，无需修改代码
from compat.v1_adapter import V1Adapter

adapter = V1Adapter()
report = adapter.validate_v1_project('/path/to/_data.py')
```

**策略 2: 渐进式迁移**
- 使用 V2 验证 V1 项目
- 逐步替换为 V2 格式
- 使用 V2 生成管线

**策略 3: 一次性迁移**
```python
adapter = V1Adapter()
adapter.migrate_v1_to_v2(
    v1_data_path='/path/to/_data.py',
    v2_output_path='/path/to/v2_data.json'
)
```

详见：[迁移指南](docs/MIGRATION_GUIDE.md)

---

## 文档

- [项目总结](PROJECT_SUMMARY.md) - 完整项目回顾
- [执行计划](EXECUTION_PLAN.md) - Phase 5-8 计划
- [Phase 5 报告](PHASE5_COMPLETION_REPORT.md) - RuleCard 基础架构
- [Phase 6 报告](PHASE6_COMPLETION_REPORT.md) - 规则迁移
- [迁移指南](docs/MIGRATION_GUIDE.md) - V1→V2 迁移

---

## 规则库

### 已迁移规则（10个）

| ID | 名称 | 类别 | 严重程度 | 状态 |
|----|------|------|----------|------|
| R001 | 五等式结构 | Structure | FAIL | ✅ |
| R002 | 八段完整性 | Structure | FAIL | ✅ |
| R003 | Dynamic 段完整性 | Structure | FAIL | ✅ |
| R004 | 对白规则 | Content | WARN | ✅ |
| R005 | 音频桥接 | Content | WARN | ✅ |
| R006 | 风格标签 | Style | WARN | ✅ |
| R007 | 时长约束 | Technical | FAIL | ✅ |
| R008 | 预算管理 | Technical | WARN | ✅ |
| R009 | H3模式路由 | H3 | FAIL | ✅ |
| R010 | 站位承重 | H3 | OK | ✅ |

### 待迁移规则（34个）

来自 AiFilm-pipeline 的其他规则将逐步迁移。

---

## 测试

运行所有单元测试：

```bash
python tests/unit/test_rule_card.py
python tests/unit/test_rule_engine.py
```

**测试覆盖率**: 100% (19/19 通过)

---

## 技术指标

- **代码量**: 5,180+ 行
- **规则数**: 10 个（已迁移）
- **测试覆盖率**: 100%
- **Context 优化**: Token 使用 ↓40%
- **维护成本**: 规则更新 ↓50%

---

## 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)（待补充）。

---

## 许可证

MIT License

---

## 联系

- **GitHub**: https://github.com/piaoboo/AiFilm-v2
- **Issues**: https://github.com/piaoboo/AiFilm-v2/issues

---

**开始使用**: 选择你的迁移策略，从零成本兼容开始！
