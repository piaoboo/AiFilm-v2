#!/usr/bin/env python3
"""
无台词密度规则

检查无台词镜头的比例：
- 15s 滚动窗口内"冷场镜"（无台词 + 非奇观 + 未标类型）> 上限 → WARN
- 冷场镜定义：无台词 + VFX C 裸镜 + 未标类型

迁移自: AiFilm-pipeline validators.py _g18_silent_density
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 冷场镜阈值（15s 窗口内）
COLD_SHOT_THRESHOLD = 0.5  # 50%


def check_silent_density(model):
    """
    检查无台词密度

    Args:
        model: 包含 shots 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    shots = getattr(model, 'shots', [])
    qc_present = getattr(model, 'qc_present', False)

    if not qc_present:
        return [(Severity.OK, "无台词密度校验跳过:无 SHOT_QC → 旧集宽容")]

    if len(shots) < 3:
        return [(Severity.OK, "镜头数不足，跳过密度检查")]

    # 识别冷场镜
    cold_shots = []
    for shot in shots:
        shot_id = shot.get('id', '?')
        dialogue_count = shot.get('dialogue_count', 0)
        vfx_grade = shot.get('vfx_grade', 'C')
        shot_type = shot.get('shot_type', '')

        # 冷场镜：无台词 + VFX C + 未标类型
        is_cold = (
            dialogue_count == 0 and
            vfx_grade == 'C' and
            not shot_type
        )

        if is_cold:
            cold_shots.append(shot_id)

    # 计算冷场比例
    cold_ratio = len(cold_shots) / len(shots) if shots else 0

    if cold_ratio > COLD_SHOT_THRESHOLD:
        return [(
            Severity.WARN,
            f"冷场镜密度过高: {len(cold_shots)}/{len(shots)} ({cold_ratio:.0%}) "
            f"→ 建议添加台词或标记类型"
        )]
    else:
        return [(Severity.OK, f"冷场镜密度正常: {len(cold_shots)}/{len(shots)} ({cold_ratio:.0%})")]


# 创建规则卡片
rule_silent_density = content_rule(
    id="R018",
    name="无台词密度",
    rule=check_silent_density,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查无台词镜头的比例，防止冷场",
    examples=[
        '✅ 10 个镜头，3 个冷场镜（30%）',
        '⚠️ 10 个镜头，8 个冷场镜（80%）→ WARN'
    ],
    rationale="对白是叙事的重要手段，过多冷场镜可能导致观众流失",
    references=["AiFilm-pipeline/code/validators.py:_g18_silent_density"],
    priority=60,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("无台词密度规则测试")
    print("=" * 60)

    # 测试1: 密度正常
    class PassModel:
        qc_present = True
        shots = [
            {'id': 'SH01', 'dialogue_count': 5, 'vfx_grade': 'C'},
            {'id': 'SH02', 'dialogue_count': 0, 'vfx_grade': 'S'},  # 奇观镜，不算冷场
            {'id': 'SH03', 'dialogue_count': 0, 'vfx_grade': 'C', 'shot_type': ''},  # 冷场镜
        ]

    result = rule_silent_density.apply(PassModel())
    print(f"\n测试1 - 密度正常:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 密度过高
    class WarnModel:
        qc_present = True
        shots = [
            {'id': 'SH01', 'dialogue_count': 0, 'vfx_grade': 'C', 'shot_type': ''},
            {'id': 'SH02', 'dialogue_count': 0, 'vfx_grade': 'C', 'shot_type': ''},
            {'id': 'SH03', 'dialogue_count': 5, 'vfx_grade': 'C'},
        ]

    result = rule_silent_density.apply(WarnModel())
    print(f"\n测试2 - 密度过高:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
