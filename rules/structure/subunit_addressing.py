#!/usr/bin/env python3
"""
子单元编号连续性规则

检查子单元编号是否连续：
- 子单元号必须从 1 开始连续递增
- 键集不能超集（防止镜号空间残留）

迁移自: AiFilm-pipeline validators.py _g22_subunit_addressing
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import structure_rule, Severity


def check_subunit_addressing(model):
    """
    检查子单元编号连续性

    Args:
        model: 包含 subunit_keys, subunit_table_keys 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_keys = getattr(model, 'subunit_keys', [])
    subunit_table_keys = getattr(model, 'subunit_table_keys', {})

    if not subunit_keys or not subunit_table_keys:
        return [(Severity.OK, "无子单元结构，跳过编号检查")]

    results = []

    # 检查连续性
    expected = list(range(1, len(subunit_keys) + 1))
    if subunit_keys != expected:
        results.append((
            Severity.FAIL,
            f"子单元编号不连续: {subunit_keys} → 应为 {expected}"
        ))

    # 检查键集超集
    for table_name, table_keys in subunit_table_keys.items():
        if not isinstance(table_keys, (list, set)):
            continue

        extra_keys = set(table_keys) - set(subunit_keys)
        if extra_keys:
            results.append((
                Severity.FAIL,
                f"{table_name} 存在超集键: {sorted(extra_keys)} → 镜号空间残留"
            ))

    if not results:
        return [(Severity.OK, f"子单元编号连续({len(subunit_keys)}个子单元)")]

    return results


# 创建规则卡片
rule_subunit_addressing = structure_rule(
    id="R021",
    name="子单元编号连续性",
    rule=check_subunit_addressing,
    validate=lambda output: output,
    description="检查子单元编号是否连续，防止镜号空间残留",
    examples=[
        '✅ 子单元编号 [1, 2, 3, 4]',
        '❌ 子单元编号 [1, 3, 4] → FAIL (缺 2)'
    ],
    rationale="合并子单元时必须更新所有子单元级表，防止数据残留",
    references=["AiFilm-pipeline/code/validators.py:_g22_subunit_addressing"],
    priority=85,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("子单元编号连续性规则测试")
    print("=" * 60)

    # 测试1: 编号连续
    class PassModel:
        subunit_keys = [1, 2, 3, 4]
        subunit_table_keys = {
            'subunit_meta': [1, 2, 3, 4],
            'subunit_assets': [1, 2, 3, 4],
        }

    result = rule_subunit_addressing.apply(PassModel())
    print(f"\n测试1 - 编号连续:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 编号不连续
    class FailModel1:
        subunit_keys = [1, 3, 4]
        subunit_table_keys = {
            'subunit_meta': [1, 3, 4],
        }

    result = rule_subunit_addressing.apply(FailModel1())
    print(f"\n测试2 - 编号不连续:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 键集超集
    class FailModel2:
        subunit_keys = [1, 2, 3]
        subunit_table_keys = {
            'subunit_meta': [1, 2, 3, 4, 5],  # 4, 5 是镜号空间残留
        }

    result = rule_subunit_addressing.apply(FailModel2())
    print(f"\n测试3 - 键集超集:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
