#!/usr/bin/env python3
"""
木头人检查规则

检查是否"挂图但散文无动作"（木头人）：
- 图片引用存在，但 Dynamic 段没有描述该角色动作
- 只挂图不写动作，模型会渲染成静态背景人物

迁移自: AiFilm-pipeline validators.py _g16_woody
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_woody(model):
    """
    检查木头人

    Args:
        model: 包含以下属性的模型对象
            - subunit_assets: {subunit_id: [角色列表]}
            - prompt_blocks: prompt 文本块列表

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_assets = getattr(model, 'subunit_assets', {})
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not subunit_assets:
        return [(Severity.OK, "无子单元资产数据，跳过木头人检查")]

    woody_cases = []

    for subunit_id, assets in subunit_assets.items():
        if len(assets) < 2:
            continue

        block_text = str(prompt_blocks[subunit_id - 1]) if subunit_id <= len(prompt_blocks) else ''

        # 检查每个角色是否在散文中出现
        for char in assets:
            if char not in block_text:
                woody_cases.append(f"SU{subunit_id}:{char}")

    if woody_cases:
        return [(
            Severity.WARN,
            f"疑似木头人: {', '.join(woody_cases)} → 核对是否需要补充动作"
        )]
    else:
        return [(Severity.OK, "无木头人风险")]


# 创建规则卡片
rule_woody = content_rule(
    id="R028",
    name="木头人检查",
    rule=check_woody,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查是否'挂图但散文无动作'（木头人）",
    examples=[
        '⚠️ SHOT_ASSETS 含张三，但 Dynamic 没提张三 → WARN',
        '✅ SHOT_ASSETS 含张三，Dynamic 写"张三推门进入"'
    ],
    rationale="只挂图不写动作，模型会渲染成静态背景人物（木头人）",
    references=["AiFilm-pipeline/code/validators.py:_g16_woody"],
    priority=60,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("木头人检查规则测试")
    print("=" * 60)

    # 测试1: 无木头人
    class PassModel:
        subunit_assets = {1: ["张三", "李四"]}
        prompt_blocks = ["Dynamic: 张三与李四对话"]

    result = rule_woody.apply(PassModel())
    print(f"\n测试1 - 无木头人:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 疑似木头人
    class WarnModel:
        subunit_assets = {1: ["张三", "李四"]}
        prompt_blocks = ["Dynamic: 张三推门进入"]

    result = rule_woody.apply(WarnModel())
    print(f"\n测试2 - 疑似木头人:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
