#!/usr/bin/env python3
"""
道具一致性规则

验证场景道具的声明与使用一致性：
1. 道具在使用前必须声明
2. 避免道具凭空出现

迁移自: AiFilm-pipeline validators.py _g47_props_consistency
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 常见道具关键词
PROP_KEYWORDS = [
    '杯子', '咖啡杯', '茶杯', '椅子', '桌子', '门', '窗', '钥匙',
    '手机', '电脑', '笔', '书', '眼镜', '包', '伞', '刀', '剑',
]


def check_props_consistency(model):
    """
    检查道具一致性

    Args:
        model: 包含以下属性的模型对象
            - shots: 镜头列表
            - prompt_blocks: prompt 文本块列表

    Returns:
        List[tuple]: 验证结果列表
    """
    shots = getattr(model, 'shots', [])
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not shots or not prompt_blocks:
        return [(Severity.OK, "无数据，跳过道具一致性检查")]

    declared_props = set()
    undeclared_uses = []

    for i, shot in enumerate(shots):
        shot_id = shot.get('id', f'SH{i+1}')
        props = shot.get('props', [])
        block_text = str(prompt_blocks[i]) if i < len(prompt_blocks) else ''

        # 记录声明的道具
        declared_props.update(props)

        # 检查使用的道具
        for prop_keyword in PROP_KEYWORDS:
            if prop_keyword in block_text and prop_keyword not in declared_props:
                undeclared_uses.append(f"{shot_id}使用'{prop_keyword}'")

    if undeclared_uses:
        return [(
            Severity.WARN,
            f"道具未声明: {', '.join(undeclared_uses)} → 建议在 props 中声明"
        )]
    else:
        return [(Severity.OK, f"道具一致性通过({len(declared_props)}个道具)")]


# 创建规则卡片
rule_props_consistency = content_rule(
    id="R031",
    name="道具一致性",
    rule=check_props_consistency,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="验证场景道具的声明与使用一致性",
    examples=[
        '✅ SH01 props=[\'杯子\'], SH02 使用\'杯子\'',
        '❌ SH01 无 props, SH02 使用\'杯子\' → WARN'
    ],
    rationale="道具一致性是视觉连续性的基础",
    references=["AiFilm-pipeline/code/validators.py:_g47_props_consistency"],
    priority=60,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("道具一致性规则测试")
    print("=" * 60)

    # 测试1: 一致性通过
    class PassModel:
        shots = [
            {'id': 'SH01', 'props': ['杯子']},
            {'id': 'SH02', 'props': []},
        ]
        prompt_blocks = [
            "桌上有杯子",
            "杯子放在桌上",
        ]

    result = rule_props_consistency.apply(PassModel())
    print(f"\n测试1 - 一致性通过:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 道具未声明
    class WarnModel:
        shots = [
            {'id': 'SH01', 'props': []},
            {'id': 'SH02', 'props': []},
        ]
        prompt_blocks = [
            "空镜",
            "拿起桌上的杯子",
        ]

    result = rule_props_consistency.apply(WarnModel())
    print(f"\n测试2 - 道具未声明:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
