#!/usr/bin/env python3
"""
Dynamic 段完整性规则

禁止 Dynamic 段使用省略或箭头流水账：
- 禁止: (略) / 同上 / 结构同上 / 结构同镜N
- 禁止: 箭头流水账（多个 → 连用）

迁移自: AiFilm-pipeline validators.py _g03_dynamic
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import structure_rule, Severity


def check_dynamic_completeness(model):
    """
    检查 Dynamic 段完整性

    Args:
        model: 包含 prompt_blocks 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    violations = []

    # 省略模式
    omit_patterns = [
        r'\(略\)',
        r'同上',
        r'结构同上',
        r'结构同镜\d+',
    ]

    # 箭头流水账模式（连续3个以上箭头）
    arrow_pattern = r'(→.*?){3,}'

    for i, block in enumerate(prompt_blocks):
        block_text = str(block) if not isinstance(block, str) else block

        # 检查省略
        for pattern in omit_patterns:
            if re.search(pattern, block_text):
                violations.append(f"块{i+1}: 发现省略 '{pattern}'")

        # 检查箭头流水账
        if re.search(arrow_pattern, block_text):
            violations.append(f"块{i+1}: 箭头流水账（连续多个→）")

    if violations:
        return [(
            Severity.FAIL,
            "Dynamic 段不完整: " + "; ".join(violations[:3]) +
            (f" ...另{len(violations)-3}处" if len(violations) > 3 else "")
        )]
    else:
        return [(Severity.OK, "Dynamic 段完整性通过")]


# 创建规则卡片
rule_dynamic_completeness = structure_rule(
    id="R003",
    name="Dynamic 段完整性",
    rule=check_dynamic_completeness,
    validate=lambda output: output,
    description="禁止 Dynamic 段使用省略或箭头流水账",
    examples=[
        '✅ "侦探推开车门，走向公交车站，目光扫过街道"',
        '❌ "侦探(略)" → FAIL',
        '❌ "推门→走路→回头" → FAIL (箭头流水账)'
    ],
    rationale="省略和流水账会导致 prompt 不完整，影响视频生成质量",
    references=["AiFilm-pipeline/code/validators.py:_g03_dynamic"],
    priority=90,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("Dynamic 段完整性规则测试")
    print("=" * 60)

    # 测试1: 正常
    class PassModel:
        prompt_blocks = [
            "Dynamic: 侦探推开车门，走向公交车站，目光扫过街道"
        ]

    result = rule_dynamic_completeness.apply(PassModel())
    print(f"\n测试1 - 正常描述:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 省略
    class OmitModel:
        prompt_blocks = [
            "Dynamic: 侦探推开车门(略)，走向公交车站"
        ]

    result = rule_dynamic_completeness.apply(OmitModel())
    print(f"\n测试2 - 包含省略:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 箭头流水账
    class ArrowModel:
        prompt_blocks = [
            "Dynamic: 推门→走路→回头→坐下"
        ]

    result = rule_dynamic_completeness.apply(ArrowModel())
    print(f"\n测试3 - 箭头流水账:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
