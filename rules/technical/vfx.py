#!/usr/bin/env python3
"""
VFX 级别规则

检查 VFX 级别是否符合标准 enum：
- S: 核心叙事特效（必须完美）
- A: 重要特效
- B: 常规特效
- C: 背景特效
- N/A: 无特效

迁移自: AiFilm-pipeline validators.py _g08_vfx
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity

# VFX 级别枚举
VFX_GRADES = {"S", "A", "B", "C", "N/A"}


def check_vfx(model):
    """
    检查 VFX 级别

    Args:
        model: 包含 shots 或 qc_present 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    qc_present = getattr(model, 'qc_present', False)
    shots = getattr(model, 'shots', [])

    if not qc_present:
        return [(Severity.WARN, "VFX 级别校验跳过:无 SHOT_QC(VFX) → 旧集宽容,新集应补")]

    # 检查每个镜头的 VFX 级别
    invalid = []
    for shot in shots:
        shot_id = shot.get('id', '?')
        vfx_grade = shot.get('vfx_grade', shot.get('VFX', ''))

        if vfx_grade not in VFX_GRADES:
            invalid.append(f"{shot_id}='{vfx_grade}'")

    if invalid:
        return [(
            Severity.FAIL,
            f"VFX 级别非法: {', '.join(invalid)} → 必须 ∈ {{S, A, B, C, N/A}}"
        )]
    else:
        return [(Severity.OK, f"VFX 级别全合法({len(shots)}个镜头)")]


# 创建规则卡片
rule_vfx = technical_rule(
    id="R016",
    name="VFX 级别",
    rule=check_vfx,
    validate=lambda output: output,
    description="检查 VFX 级别是否符合标准 enum",
    examples=[
        '✅ vfx_grade="S"',
        '❌ vfx_grade="高" → FAIL'
    ],
    rationale="VFX 级别决定制作排期，必须用标准 enum",
    references=["AiFilm-pipeline/code/validators.py:_g08_vfx"],
    priority=75,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("VFX 级别规则测试")
    print("=" * 60)

    # 测试1: 合法级别
    class PassModel:
        qc_present = True
        shots = [
            {'id': 'SH01', 'vfx_grade': 'S'},
            {'id': 'SH02', 'vfx_grade': 'A'},
            {'id': 'SH03', 'vfx_grade': 'N/A'},
        ]

    result = rule_vfx.apply(PassModel())
    print(f"\n测试1 - 合法级别:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 非法级别
    class FailModel:
        qc_present = True
        shots = [
            {'id': 'SH01', 'vfx_grade': 'S'},
            {'id': 'SH02', 'vfx_grade': '高'},
        ]

    result = rule_vfx.apply(FailModel())
    print(f"\n测试2 - 非法级别:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
