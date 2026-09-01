#!/usr/bin/env python3
"""
八段完整性规则

检查 castSpell 八段标签是否齐全：
每段标签覆盖数 ≥ 视频prompt 数

八段: SHOT_META, Dynamic, Static, Camera, Optics, Style & Mood, Audio, SHOT_ASSETS

迁移自: AiFilm-pipeline validators.py _g02_eight_seg
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import structure_rule, Severity

# 八段标签定义
EIGHT_TOKENS = [
    "SHOT_META",
    "Dynamic",
    "Static",
    "Camera",
    "Optics",
    "Style & Mood",
    "Audio",
    "SHOT_ASSETS"
]


def count_segment_coverage(prompt_blocks, label):
    """
    计算标签在块中的覆盖数（每块最多记1次）

    Args:
        prompt_blocks: prompt 块列表
        label: 要检查的标签

    Returns:
        int: 覆盖的块数
    """
    count = 0
    for block in prompt_blocks:
        block_text = str(block) if not isinstance(block, str) else block
        if label in block_text:
            count += 1
    return count


def check_eight_segments(model):
    """
    检查八段完整性

    Args:
        model: 包含以下属性的模型对象
            - prompt_blocks: prompt 块列表
            - n_vid: 视频prompt数

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    n_vid = getattr(model, 'n_vid', 0)

    if not n_vid:
        return [(Severity.OK, "无视频prompt，跳过八段检查")]

    seg_fail = []

    for segment in EIGHT_TOKENS:
        coverage = count_segment_coverage(prompt_blocks, segment)
        if coverage < n_vid:
            seg_fail.append(f"{segment}({coverage}<{n_vid})")

    if seg_fail:
        return [(
            Severity.FAIL,
            "八段缺漏: " + ", ".join(seg_fail) + " → 回 F3/Q3"
        )]
    else:
        return [(
            Severity.OK,
            f"八段标签覆盖齐(每段≥{n_vid})"
        )]


# 创建规则卡片
rule_eight_segments = structure_rule(
    id="R002",
    name="八段完整性",
    rule=check_eight_segments,
    validate=lambda output: output,
    description="检查 castSpell 八段标签是否齐全：每段标签覆盖数 ≥ 视频prompt 数",
    examples=[
        "✅ 每段都出现 ≥ N 次（N = 视频prompt数）",
        "❌ Dynamic 只出现 3 次，但有 5 个 prompt → FAIL '八段缺漏'"
    ],
    rationale="castSpell 八段是 SSOT 结构锁，缺漏会导致 prompt 不完整",
    references=["AiFilm-pipeline/code/validators.py:_g02_eight_seg"],
    priority=95,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("八段完整性规则测试")
    print("=" * 60)

    # 测试用例1: 八段齐全
    class PassModel:
        n_vid = 3
        prompt_blocks = [
            "SHOT_META: xxx\nDynamic: xxx\nStatic: xxx\nCamera: xxx\nOptics: xxx\nStyle & Mood: xxx\nAudio: xxx\nSHOT_ASSETS: xxx",
            "SHOT_META: yyy\nDynamic: yyy\nStatic: yyy\nCamera: yyy\nOptics: yyy\nStyle & Mood: yyy\nAudio: yyy\nSHOT_ASSETS: yyy",
            "SHOT_META: zzz\nDynamic: zzz\nStatic: zzz\nCamera: zzz\nOptics: zzz\nStyle & Mood: zzz\nAudio: zzz\nSHOT_ASSETS: zzz",
        ]

    result = rule_eight_segments.apply(PassModel())
    print(f"\n测试1 - 八段齐全:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试用例2: 缺少 Dynamic
    class FailModel:
        n_vid = 3
        prompt_blocks = [
            "SHOT_META: xxx\nStatic: xxx\nCamera: xxx\nOptics: xxx\nStyle & Mood: xxx\nAudio: xxx\nSHOT_ASSETS: xxx",
            "SHOT_META: yyy\nDynamic: yyy\nStatic: yyy\nCamera: yyy\nOptics: yyy\nStyle & Mood: yyy\nAudio: yyy\nSHOT_ASSETS: yyy",
            "SHOT_META: zzz\nStatic: zzz\nCamera: zzz\nOptics: zzz\nStyle & Mood: zzz\nAudio: zzz\nSHOT_ASSETS: zzz",
        ]

    result = rule_eight_segments.apply(FailModel())
    print(f"\n测试2 - 缺少 Dynamic:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
