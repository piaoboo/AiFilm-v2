#!/usr/bin/env python3
"""
Loop 经济性指标规则

检查 Loop 循环次数是否经济：
- Loop 次数建议 ≤ 3
- 过多 Loop 增加成本

迁移自: AiFilm-pipeline validators.py _g15_loop_metrics
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory

# Loop 指标必需字段
LOOP_METRICS_FIELDS = [
    "total_loops",
    "accepted",
    "rejected",
    "acceptance_rate",
]

# Loop 次数建议上限
LOOP_THRESHOLD = 3


def check_loop_metrics(model):
    """
    检查 Loop 经济性指标

    Args:
        model: 包含 loop_metrics 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    loop_metrics = getattr(model, 'loop_metrics', None)

    if not loop_metrics:
        return [(Severity.OK, "loop-metrics 未填(默认∅态,不阻塞交付)")]

    if not isinstance(loop_metrics, dict):
        return [(Severity.WARN, f"loop-metrics 格式非法(须为 dict)")]

    # 检查必需字段
    missing = [k for k in LOOP_METRICS_FIELDS if not str(loop_metrics.get(k, "")).strip()]

    if missing:
        return [(
            Severity.WARN,
            f"loop-metrics 块缺字段: {', '.join(missing)} → 补全后才能算接受率"
        )]

    # 检查 Loop 次数
    total_loops = loop_metrics.get('total_loops', 0)
    try:
        total_loops = int(total_loops)
    except (ValueError, TypeError):
        return [(Severity.WARN, f"total_loops 格式非法: {total_loops}")]

    if total_loops > LOOP_THRESHOLD:
        return [(
            Severity.WARN,
            f"Loop 次数过多: {total_loops} 次 → 建议 ≤{LOOP_THRESHOLD} 次"
        )]
    else:
        return [(Severity.OK, f"Loop 经济性合理({total_loops} 次)")]


# 创建规则卡片
rule_loop_metrics = RuleCard(
    id="R027",
    name="Loop 经济性指标",
    category=RuleCategory.TECHNICAL,
    rule=check_loop_metrics,
    severity=Severity.WARN,
    description="检查 Loop 循环次数是否经济",
    examples=[
        '✅ Loop 2 次（合理）',
        '⚠️ Loop 5 次 → WARN'
    ],
    rationale="每次 Loop 都消耗 API 调用，成本线性增长",
    references=["AiFilm-pipeline/code/validators.py:_g15_loop_metrics"],
    priority=50,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("Loop 经济性指标规则测试")
    print("=" * 60)

    # 测试1: 经济合理
    class PassModel:
        loop_metrics = {
            'total_loops': 2,
            'accepted': 2,
            'rejected': 0,
            'acceptance_rate': 1.0,
        }

    result = rule_loop_metrics.apply(PassModel())
    print(f"\n测试1 - 经济合理:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: Loop 过多
    class WarnModel:
        loop_metrics = {
            'total_loops': 5,
            'accepted': 3,
            'rejected': 2,
            'acceptance_rate': 0.6,
        }

    result = rule_loop_metrics.apply(WarnModel())
    print(f"\n测试2 - Loop 过多:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
