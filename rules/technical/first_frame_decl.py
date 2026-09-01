#!/usr/bin/env python3
"""
首帧声明规则

检查首帧/尾帧声明的位置与编号：
1. 位置：必须在 Prompt 第一句
2. 编号：必须用上传顺序号（图片1/图片2...）

迁移自: AiFilm-pipeline validators.py _g29_first_frame_decl
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory


def check_first_frame_decl(model):
    """
    检查首帧声明

    Args:
        model: 包含以下属性的模型对象
            - prompt_blocks: prompt 文本块列表
            - asset_count: 资产数量

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not prompt_blocks:
        return [(Severity.OK, "无 prompt 块，跳过首帧声明检查")]

    violations = []

    for i, block in enumerate(prompt_blocks, 1):
        block_text = str(block)
        lines = block_text.strip().split('\n')

        if not lines:
            continue

        first_line = lines[0]

        # 检查是否有首帧/尾帧声明
        frame_match = re.search(r'(首帧|尾帧).*?图片(\d+)', block_text)

        if not frame_match:
            continue

        frame_type = frame_match.group(1)
        frame_num = int(frame_match.group(2))

        # 检查位置：必须在第一句
        if frame_match.group(0) not in first_line:
            violations.append(f"块{i}:{frame_type}声明不在第一句")

        # 检查编号：不能超过资产数
        asset_count = getattr(model, 'asset_count', 10)
        if frame_num > asset_count:
            violations.append(f"块{i}:图片{frame_num}超过资产数{asset_count}")

    if violations:
        return [(
            Severity.WARN,
            f"首帧声明违规: {'; '.join(violations)} → 修正位置和编号"
        )]
    else:
        return [(Severity.OK, "首帧声明正确")]


# 创建规则卡片
rule_first_frame_decl = RuleCard(
    id="R047",
    name="首帧声明",
    category=RuleCategory.TECHNICAL,
    rule=check_first_frame_decl,
    severity=Severity.WARN,
    description="检查首帧/尾帧声明的位置与编号",
    examples=[
        '✅ "图片1为首帧。Dynamic: ..." → 正确',
        '❌ "Dynamic: ... 图片83为首帧" → 位置错误',
        '❌ "图片83为首帧" 但只有2张图 → 编号超范围'
    ],
    rationale="首帧声明必须在第一句，且编号必须正确，否则无法锁定首帧",
    references=["AiFilm-pipeline/code/validators.py:_g29_first_frame_decl"],
    priority=75,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("首帧声明规则测试")
    print("=" * 60)

    # 测试1: 正确声明
    class PassModel:
        prompt_blocks = ["图片1为首帧。Dynamic: 场景描述"]
        asset_count = 5

    result = rule_first_frame_decl.apply(PassModel())
    print(f"\n测试1 - 正确声明:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 位置错误
    class WarnModel1:
        prompt_blocks = ["Dynamic: 场景描述。图片1为首帧"]
        asset_count = 5

    result = rule_first_frame_decl.apply(WarnModel1())
    print(f"\n测试2 - 位置错误:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 编号超范围
    class WarnModel2:
        prompt_blocks = ["图片83为首帧。Dynamic: 场景描述"]
        asset_count = 2

    result = rule_first_frame_decl.apply(WarnModel2())
    print(f"\n测试3 - 编号超范围:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
