#!/usr/bin/env python3
"""
双对比探针规则

检查相邻镜头的景别和机位运动是否重复：
- 相邻镜头景别相同 → WARN
- 相邻镜头相机模式相同 → WARN

迁移自: AiFilm-pipeline validators.py _g12_contrast
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 相机运动模式
CAMERA_MODES = [
    "推镜", "拉镜", "摇镜", "移镜", "跟镜",
    "升降", "环绕", "手持", "固定"
]


def check_contrast(model):
    """
    检查双对比（景别+机位）

    Args:
        model: 包含 shots 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    shots = getattr(model, 'shots', [])

    if len(shots) < 2:
        return [(Severity.OK, "镜头数不足2，跳过对比检查")]

    warnings = []
    prev_shot_type = None
    prev_camera_mode = None

    for i, shot in enumerate(shots):
        shot_id = shot.get('id', f'SH{i+1}')

        # 提取景别
        shot_type = shot.get('shot_type', '').upper()
        camera = shot.get('camera', '')

        # 提取相机模式
        camera_mode = None
        for mode in CAMERA_MODES:
            if mode in camera:
                camera_mode = mode
                break

        # 检查景别重复
        if prev_shot_type and shot_type == prev_shot_type:
            warnings.append(f"{shot_id}景别与上镜同({shot_type})")

        # 检查相机模式重复
        if prev_camera_mode and camera_mode and camera_mode == prev_camera_mode:
            warnings.append(f"{shot_id}相机模式与上镜同({camera_mode})")

        prev_shot_type = shot_type
        prev_camera_mode = camera_mode

    if warnings:
        return [(
            Severity.WARN,
            "双对比提示: " + "; ".join(warnings) + " → 建议换景别/机位"
        )]
    else:
        return [(Severity.OK, "双对比全过(相邻景别+模式均变)")]


# 创建规则卡片
rule_contrast = content_rule(
    id="R013",
    name="双对比探针",
    rule=check_contrast,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查相邻镜头的景别和机位运动是否重复",
    examples=[
        '⚠️ 镜2景别与上镜同(中景) → WARN',
        '✅ 相邻景别+模式均变'
    ],
    rationale="相邻镜头景别/机位重复会导致画面单调",
    references=["AiFilm-pipeline/code/validators.py:_g12_contrast"],
    priority=60,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("双对比探针规则测试")
    print("=" * 60)

    # 测试1: 对比正常
    class PassModel:
        shots = [
            {'id': 'SH01', 'shot_type': '中景', 'camera': '推镜'},
            {'id': 'SH02', 'shot_type': '特写', 'camera': '固定'},
        ]

    result = rule_contrast.apply(PassModel())
    print(f"\n测试1 - 对比正常:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 景别重复
    class WarnModel:
        shots = [
            {'id': 'SH01', 'shot_type': '中景', 'camera': '推镜'},
            {'id': 'SH02', 'shot_type': '中景', 'camera': '固定'},
        ]

    result = rule_contrast.apply(WarnModel())
    print(f"\n测试2 - 景别重复:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
