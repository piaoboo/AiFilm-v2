# AiFilm V2.0 重构执行计划

**启动日期**: 2026-09-01  
**基础**: V2UpdatePlan Phase 0-4 完成  
**方案**: 三步演化 + RuleCard 架构

---

## 项目背景

### 已完成的准备工作
- ✅ Phase 0-3: 痛点复现、H3适配层、闸升级、真实验证（V2UpdatePlan）
- ✅ Phase 4: 成果部署到 AiFilm-pipeline（2026-09-01）
- ✅ 基础设施: Gate 46-52、H3Adapter、痛点检测工具

### 当前痛点（需要重构解决）
根据委员会报告和混合方案，核心痛点是：

**A类 - 验证逻辑缺失** (已通过 Gate 46-52 部分解决)
- ✅ 多人戏站位混乱
- ✅ 同场人数盘点
- ✅ 正反打站位
- ✅ 场景道具
- ✅ 景别阶梯
- ✅ 运镜合理性

**B类 - 规则组织混乱** (待解决 ⬅️ 本次重构核心)
- ❌ 产出提示词效率低（需手动组装模块）
- ❌ 提示词逻辑不清（规则散落各处）
- ❌ Context 溢出（44个规则文件）
- ❌ 规则碎片化（人工 grep）
- ❌ 无增量测试

---

## 重构目标

### 核心目标
1. **引入 RuleCard 架构** - 统一规则表示和管理
2. **建立生成管线** - 自动化提示词组装
3. **优化 Context 管理** - 按需加载规则
4. **提升可维护性** - 规则即代码，支持增量测试

### 非目标（不在本次范围）
- ❌ 不重写现有 44 个 reference/*.md 文件
- ❌ 不改动现有 validators.py 的 39 个老闸
- ❌ 不迁移现有项目（保持向后兼容）

---

## 架构设计

### V2 核心架构

```
AiFilm-v2/
├── core/
│   ├── rule_card.py          # RuleCard 基类
│   ├── rule_engine.py        # 规则引擎
│   ├── context_manager.py    # Context 管理
│   └── pipeline.py           # 生成管线
├── rules/
│   ├── structure/            # 结构规则（五等式、八段等）
│   ├── style/                # 风格规则（风格标签、署名等）
│   ├── content/              # 内容规则（对白、动作等）
│   ├── technical/            # 技术规则（时长、预算等）
│   └── h3/                   # H3 专用规则
├── adapters/
│   ├── seedance_adapter.py   # Seedance 2.5 适配器
│   └── h3_adapter.py         # H3 适配器（已有）
├── validators/
│   ├── gate_registry.py      # 闸注册表
│   └── gate_runner.py        # 闸执行器
├── tests/
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试夹具
└── examples/
    ├── seedance_project/     # Seedance 示例项目
    └── h3_project/           # H3 示例项目
```

### RuleCard 设计

```python
class RuleCard:
    """规则卡片基类"""
    
    # 元数据
    id: str                    # 规则ID（唯一）
    name: str                  # 规则名称
    category: str              # 类别（structure/style/content/technical）
    priority: int              # 优先级（1-100）
    version: str               # 版本号
    
    # 条件
    when: Callable             # 触发条件
    applies_to: List[str]      # 适用范围（seedance/h3/all）
    
    # 规则内容
    rule: Callable             # 规则逻辑
    template: Optional[str]    # 模板（用于生成）
    
    # 验证
    validate: Optional[Callable]  # 验证函数（可选）
    severity: str              # 严重程度（FAIL/WARN/INFO）
    
    # 文档
    description: str           # 规则描述
    examples: List[str]        # 示例
    rationale: str             # 设计理由
```

---

## 实施路线

### Phase 5: RuleCard 基础架构（Week 1-2，预计 16h）

**目标**: 建立 RuleCard 框架和核心引擎

**任务**:
1. 实现 RuleCard 基类
2. 实现规则引擎（加载、匹配、执行）
3. 实现 Context 管理器（按需加载）
4. 编写单元测试

**交付物**:
- `core/rule_card.py`
- `core/rule_engine.py`
- `core/context_manager.py`
- 测试覆盖率 ≥80%

**验收标准**:
- ✅ 可以定义和加载 RuleCard
- ✅ 规则引擎可以根据条件匹配规则
- ✅ Context 管理器可以按需加载规则子集
- ✅ 所有单元测试通过

---

### Phase 6: 规则迁移（Week 3-4，预计 20h）

**目标**: 将关键规则迁移为 RuleCard

**迁移策略**:
- **优先级**: 从 Top 10 痛点对应的规则开始
- **增量**: 每次迁移 5-10 个规则
- **验证**: 迁移后与原规则行为一致

**迁移清单** (第一批 10 个规则):
1. 五等式结构 (rule-core.md)
2. 八段标签 (rule-core.md)
3. Dynamic 省略 (rule-core.md)
4. 对白规则 (dialogue-diction.md)
5. 音频桥接 (rule-core.md)
6. 风格标签 (rule-core.md)
7. 时长约束 (rule-core.md)
8. 预算管理 (rule-core.md)
9. H3 模式路由 (已有 Gate 46)
10. 站位承重 (已有 H3Adapter)

**交付物**:
- `rules/structure/` (4个规则)
- `rules/content/` (2个规则)
- `rules/technical/` (2个规则)
- `rules/h3/` (2个规则)
- 集成测试

**验收标准**:
- ✅ 10 个规则迁移完成
- ✅ 与原规则行为一致（对比测试）
- ✅ 生成结果一致性 ≥95%

---

### Phase 7: 生成管线（Week 5-6，预计 16h）

**目标**: 建立自动化提示词生成管线

**功能**:
1. **规则组装**: 根据项目类型自动选择规则
2. **提示词生成**: 根据规则生成提示词
3. **验证**: 自动运行所有适用的闸
4. **报告**: 生成验证报告

**交付物**:
- `core/pipeline.py`
- `adapters/seedance_adapter.py` (完善)
- `adapters/h3_adapter.py` (集成)
- 端到端测试

**验收标准**:
- ✅ 可以从 _data.py 自动生成提示词
- ✅ Seedance 和 H3 分别生成正确格式
- ✅ 自动运行所有验证闸
- ✅ 生成验证报告

---

### Phase 8: 兼容层与迁移（Week 7-8，预计 12h）

**目标**: 与现有 AiFilm-pipeline 兼容

**任务**:
1. 实现 V1 → V2 适配器
2. 支持混合模式（V1 + V2 规则共存）
3. 迁移指南文档
4. 示例项目

**交付物**:
- `compat/v1_adapter.py`
- `docs/migration_guide.md`
- `examples/seedance_project/`
- `examples/h3_project/`

**验收标准**:
- ✅ 现有项目可以无缝使用 V2
- ✅ 迁移指南清晰可操作
- ✅ 示例项目可以运行

---

## 成功指标

### 量化指标
1. **效率提升**: 提示词生成时间 ↓60%（从手动 30min → 自动 12min）
2. **Context 优化**: 规则加载 token 数 ↓40%（按需加载）
3. **可维护性**: 规则更新成本 ↓50%（统一接口）
4. **测试覆盖**: 代码覆盖率 ≥80%

### 质量指标
1. **向后兼容**: 现有项目 100% 可用
2. **行为一致**: 迁移规则与原规则行为一致性 ≥95%
3. **稳定性**: 端到端测试通过率 100%

---

## 风险管理

### 技术风险

**风险1**: RuleCard 抽象不够灵活
- **概率**: 30%
- **影响**: 高
- **缓解**: 先实现 10 个规则，验证架构再扩展

**风险2**: Context 管理复杂度超预期
- **概率**: 40%
- **影响**: 中
- **缓解**: 优先实现简单版本（静态加载），后续优化

**风险3**: 迁移成本过高
- **概率**: 50%
- **影响**: 中
- **缓解**: 保留 V1 兼容层，渐进式迁移

### 项目风险

**风险4**: 时间估算不足
- **概率**: 60%
- **影响**: 中
- **缓解**: 每个 Phase 独立交付，可调整优先级

---

## 下一步行动

### 立即行动（今天）
1. ✅ 创建 AiFilm-v2 项目目录
2. ⬜ 实现 RuleCard 基类
3. ⬜ 实现规则引擎核心

### 本周目标
- 完成 Phase 5（RuleCard 基础架构）
- 单元测试覆盖率 ≥80%

---

**准备就绪。开始 Phase 5。**
