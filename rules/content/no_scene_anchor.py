#!/usr/bin/env python3
"""
零场景图失锚规则

检查是否有子单元缺少场景图导致失锚：
- 零场景图 + 包含 WS/MS 景别 + 非反打镜 → WARN
- 场景图缺失会导致模型继承上一子单元场景

迁移自: AiFilm-pipeline validators.py _g24_no_scene_anchor
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_no_scene_anchor(model):
    """
    检查零场景图失锚

    Args:
        model: 包含以下属性的模型对象
            - subunit_assets: {subunit_id: [资产列表]}
            - asset_types: {asset_name: type}
            - subunit_plan_range: {subunit_id: [景别列表]}
            - prompt_blocks: prompt 文本块列表

    Returns:
        List[tuple]: 验证结果列表
    """
    subunit_assets = getattr(model, 'subunit_assets', {})
    asset_types = getattr(model, 'asset_types', {})
    subunit_plan_range = getattr(model, 'subunit_plan_range', {})
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not subunit_assets:
        return [(Severity.OK, "无子单元资产数据，跳过场景锚定检查")]

    at_risk = []

    for subunit_id, assets in subunit_assets.items():
        # 统计场景图数量（排除"首帧"图）
        scene_images = [
            a for a in assets
            if asset_types.get(a, '') == 'scene' and '首帧' not in a
        ]

        if len(scene_images) > 0:
            continue

        # 检查景别
        plan_range = subunit_plan_range.get(subunit_id, [])
        has_wide = any(s in ['WS', 'MS'] for s in plan_range)

        if not has_wide:
            continue

        # 检查是否反打镜
        block_text = str(prompt_blocks[subunit_id - 1]) if subunit_id <= len(prompt_blocks) else ''
        is_reverse_shot = '反打' in block_text

        if not is_reverse_shot:
            at_risk.append(f"SU{subunit_id}")

    if at_risk:
        return [(
            Severity.WARN,
            f"零场景图失锚: {', '.join(at_risk)} → 建议添加场景图"
        )]
    else:
        return [(Severity.OK, "无零场景图失锚风险")]


# 创建规则卡片
rule_no_scene_anchor = content_rule(
    id="R023",
    name="零场景图失锚",
    rule=check_no_scene_anchor,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查是否有子单元缺少场景图导致失锚",
    examples=[
        '⚠️ SU11: 零场景图 + WS景别 + 非反打 → WARN',
        '✅ 反打镜或近景镜可以零场景图'
    ],
    rationale="场景图缺失会导致模型继承上一子单元场景，渲染错误",
    references=["AiFilm-pipeline/code/validators.py:_g24_no_scene_anchor"],
    priority=70,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("零场景图失锚规则测试")
    print("=" * 60)

    # 测试1: 有场景图
    class PassModel1:
        subunit_assets = {1: ["场景1", "角色A"]}
        asset_types = {"场景1": "scene", "角色A": "character"}
        subunit_plan_range = {1: ["WS", "MS"]}
        prompt_blocks = ["Dynamic: 宽景镜头"]

    result = rule_no_scene_anchor.apply(PassModel1())
    print(f"\n测试1 - 有场景图:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 反打镜（零场景图合法）
    class PassModel2:
        subunit_assets = {1: ["角色A"]}
        asset_types = {"角色A": "character"}
        subunit_plan_range = {1: ["WS"]}
        prompt_blocks = ["Dynamic: 反打镜头"]

    result = rule_no_scene_anchor.apply(PassModel2())
    print(f"\n测试2 - 反打镜:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 失锚风险
    class WarnModel:
        subunit_assets = {1: ["角色A"]}
        asset_types = {"角色A": "character"}
        subunit_plan_range = {1: ["WS", "MS"]}
        prompt_blocks = ["Dynamic: 宽景镜头"]

    result = rule_no_scene_anchor.apply(WarnModel())
    print(f"\n测试3 - 失锚风险:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
