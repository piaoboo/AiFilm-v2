#!/usr/bin/env python3
"""
单场景图铁律规则

检查子单元是否挂载过多场景图：
- 任一子单元挂 ≥2 张场景图 → 疑跨场景/反打污染
- 豁免：具名反打对、首帧图

迁移自: AiFilm-pipeline validators.py _g25_multi_scene_anchor
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_multi_scene_anchor(model):
    """
    检查单场景图铁律

    Args:
        model: 包含以下属性的模型对象
            - subunit_assets: {subunit_id: [资产列表]}
            - asset_types: {asset_name: type}
            - prompt_blocks: prompt 文本块列表

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_assets = getattr(model, 'subunit_assets', {})
    asset_types = getattr(model, 'asset_types', {})
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not subunit_assets:
        return [(Severity.OK, "单场景图闸跳过:无 subunit_assets 数据")]

    violations = []

    for subunit_id, assets in subunit_assets.items():
        # 统计场景图（排除首帧图）
        scene_locs = [
            a for a in assets
            if asset_types.get(a, '') == 'scene' and '首帧' not in a
        ]

        if len(scene_locs) < 2:
            continue

        # 检查是否为具名反打对
        block_text = str(prompt_blocks[subunit_id - 1]) if subunit_id <= len(prompt_blocks) else ''
        is_reverse_pair = (
            len(scene_locs) == 2 and
            '反打' in scene_locs[1] and
            '严格参考' in block_text
        )

        if not is_reverse_pair:
            violations.append(f"SU{subunit_id}({len(scene_locs)}张)")

    if violations:
        return [(
            Severity.WARN,
            f"单场景图铁律违反: {', '.join(violations)} → 疑跨场景污染"
        )]
    else:
        return [(Severity.OK, "单场景图铁律通过")]


# 创建规则卡片
rule_multi_scene_anchor = content_rule(
    id="R024",
    name="单场景图铁律",
    rule=check_multi_scene_anchor,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查子单元是否挂载过多场景图",
    examples=[
        '⚠️ SU5 挂载 3 张场景图 → WARN',
        '✅ SU7 挂载"场景+场景·反打"且有"严格参考" → 合法'
    ],
    rationale="多场景图会导致模型自行挑选，挑错会导致方向反或跨场景",
    references=["AiFilm-pipeline/code/validators.py:_g25_multi_scene_anchor"],
    priority=70,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("单场景图铁律规则测试")
    print("=" * 60)

    # 测试1: 单场景图
    class PassModel1:
        subunit_assets = {1: ["场景1", "角色A"]}
        asset_types = {"场景1": "scene", "角色A": "character"}
        prompt_blocks = ["Dynamic: 场景镜头"]

    result = rule_multi_scene_anchor.apply(PassModel1())
    print(f"\n测试1 - 单场景图:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 反打对（合法）
    class PassModel2:
        subunit_assets = {1: ["场景1", "场景1·反打"]}
        asset_types = {"场景1": "scene", "场景1·反打": "scene"}
        prompt_blocks = ["Dynamic: 严格参考场景1"]

    result = rule_multi_scene_anchor.apply(PassModel2())
    print(f"\n测试2 - 反打对:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 多场景图违规
    class WarnModel:
        subunit_assets = {1: ["场景1", "场景2", "场景3"]}
        asset_types = {"场景1": "scene", "场景2": "scene", "场景3": "scene"}
        prompt_blocks = ["Dynamic: 场景镜头"]

    result = rule_multi_scene_anchor.apply(WarnModel())
    print(f"\n测试3 - 多场景图违规:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
