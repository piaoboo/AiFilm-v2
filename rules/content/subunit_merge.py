#!/usr/bin/env python3
"""
子单元合并机会规则

检查是否有相邻子单元可以合并：
- 同场景 + 同时段 + 同角色集 + 合并后 ≤14s → 建议合并
- 合并减少子单元数，降低复杂度

迁移自: AiFilm-pipeline validators.py _g21_subunit_merge
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 子单元合并上限
MERGE_DURATION_LIMIT = 14  # 秒


def check_subunit_merge(model):
    """
    检查子单元合并机会

    Args:
        model: 包含 subunit_secs, subunit_place, subunit_chars 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_secs = getattr(model, 'subunit_secs', {})
    subunit_place = getattr(model, 'subunit_place', {})
    subunit_chars = getattr(model, 'subunit_chars', {})

    if not subunit_secs:
        return [(Severity.OK, "无子单元时长数据，跳过合并检查")]

    # 检查是否有填写场景信息
    has_place = any(p[0] for p in subunit_place.values() if isinstance(p, tuple))
    if not has_place:
        return [(Severity.OK, "无场景信息，跳过合并检查")]

    # 查找可合并的相邻对
    mergeable = []
    subunit_keys = sorted(subunit_secs.keys())

    for i in range(len(subunit_keys) - 1):
        key1 = subunit_keys[i]
        key2 = subunit_keys[i + 1]

        dur1 = subunit_secs.get(key1, 0)
        dur2 = subunit_secs.get(key2, 0)
        place1 = subunit_place.get(key1, ('', ''))
        place2 = subunit_place.get(key2, ('', ''))
        chars1 = set(subunit_chars.get(key1, []))
        chars2 = set(subunit_chars.get(key2, []))

        # 判断是否可合并
        same_location = place1[0] == place2[0] if place1[0] and place2[0] else False
        same_time = place1[1] == place2[1] if len(place1) > 1 and len(place2) > 1 else False
        same_chars = chars1 == chars2
        merged_duration = dur1 + dur2

        if (same_location and same_time and same_chars and
            merged_duration <= MERGE_DURATION_LIMIT):
            mergeable.append(f"SU{key1}+SU{key2} ({dur1}s+{dur2}s={merged_duration}s)")

    if mergeable:
        return [(
            Severity.WARN,
            f"可合并子单元: {', '.join(mergeable)} → 建议合并降低复杂度"
        )]
    else:
        return [(Severity.OK, f"无可合并子单元({len(subunit_keys)}个子单元)")]


# 创建规则卡片
rule_subunit_merge = content_rule(
    id="R020",
    name="子单元合并机会",
    rule=check_subunit_merge,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查是否有相邻子单元可以合并",
    examples=[
        '⚠️ SU1(10s) + SU2(12s) 同场景同角色 → 可合并',
        '✅ 无可合并子单元'
    ],
    rationale="过多子单元增加管理成本，能合并时建议合并",
    references=["AiFilm-pipeline/code/validators.py:_g21_subunit_merge"],
    priority=50,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("子单元合并机会规则测试")
    print("=" * 60)

    # 测试1: 可合并
    class MergeableModel:
        subunit_secs = {1: 8, 2: 6}
        subunit_place = {1: ('客厅', '白天'), 2: ('客厅', '白天')}
        subunit_chars = {1: ['A', 'B'], 2: ['A', 'B']}

    result = rule_subunit_merge.apply(MergeableModel())
    print(f"\n测试1 - 可合并:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 不可合并（场景不同）
    class NotMergeableModel:
        subunit_secs = {1: 8, 2: 6}
        subunit_place = {1: ('客厅', '白天'), 2: ('卧室', '白天')}
        subunit_chars = {1: ['A'], 2: ['A']}

    result = rule_subunit_merge.apply(NotMergeableModel())
    print(f"\n测试2 - 不可合并:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
