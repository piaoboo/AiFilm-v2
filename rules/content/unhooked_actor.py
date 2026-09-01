#!/usr/bin/env python3
"""
反向漏挂规则

检查散文中提到的角色是否挂图：
- 角色名出现在 Dynamic 散文中
- 但该子单元没有挂该角色的图
- 仅检查本集已挂过图的角色

迁移自: AiFilm-pipeline validators.py _g23_unhooked_actor
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_unhooked_actor(model):
    """
    检查反向漏挂

    Args:
        model: 包含以下属性的模型对象
            - subunit_assets: {subunit_id: [角色列表]}
            - prompt_blocks: prompt 文本块列表
            - all_characters: 本集所有已挂图角色集合

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_assets = getattr(model, 'subunit_assets', {})
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    all_characters = getattr(model, 'all_characters', set())

    if not all_characters:
        return [(Severity.OK, "无已挂图角色，跳过反向漏挂检查")]

    if not prompt_blocks:
        return [(Severity.OK, "无 prompt 块，跳过反向漏挂检查")]

    unhooked = []

    for i, block in enumerate(prompt_blocks, 1):
        block_text = str(block)
        hooked_chars = set(subunit_assets.get(i, []))

        # 检查本集已挂图的角色
        for char in all_characters:
            if char in block_text and char not in hooked_chars:
                unhooked.append(f"SU{i}缺'{char}'")

    if unhooked:
        return [(
            Severity.WARN,
            f"反向漏挂: {', '.join(unhooked)} → 散文提及但未挂图"
        )]
    else:
        return [(Severity.OK, f"无反向漏挂({len(all_characters)}个角色)")]


# 创建规则卡片
rule_unhooked_actor = content_rule(
    id="R022",
    name="反向漏挂",
    rule=check_unhooked_actor,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查散文中提到的角色是否挂图",
    examples=[
        '⚠️ Dynamic 写"叶玄转身"但未挂叶玄图 → WARN',
        '✅ 散文提及的角色都已挂图'
    ],
    rationale="主角脸无锚定，出片必串脸",
    references=["AiFilm-pipeline/code/validators.py:_g23_unhooked_actor"],
    priority=65,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("反向漏挂规则测试")
    print("=" * 60)

    # 测试1: 无漏挂
    class PassModel:
        all_characters = {"叶玄", "林薇"}
        subunit_assets = {1: ["叶玄", "林薇"]}
        prompt_blocks = ["Dynamic: 叶玄与林薇对话"]

    result = rule_unhooked_actor.apply(PassModel())
    print(f"\n测试1 - 无漏挂:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 有漏挂
    class WarnModel:
        all_characters = {"叶玄", "林薇"}
        subunit_assets = {1: ["林薇"]}
        prompt_blocks = ["Dynamic: 叶玄转身离开"]

    result = rule_unhooked_actor.apply(WarnModel())
    print(f"\n测试2 - 有漏挂:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
