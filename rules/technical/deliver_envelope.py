#!/usr/bin/env python3
"""
逐镜交付包络规则

检查每个镜头是否符合 per-model 秒数上限：
- Seedance 2.0: ≤ 14s（留 1s 手柄帧）
- Seedance 2.5: ≤ 29s（留 1s 手柄帧）
- 下限: ≥ 4s（2.5 硬地板）

迁移自: AiFilm-pipeline validators.py _g14_deliver_envelope
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity

# 模型时长上限
MODEL_CAPS = {
    "seedance-2.0": {"max": 14, "min": 4},
    "seedance-2.5": {"max": 29, "min": 4},
}


def check_deliver_envelope(model):
    """
    检查逐镜交付包络

    Args:
        model: 包含以下属性的模型对象
            - shots: 镜头列表
            - model_version: 模型版本

    Returns:
        List[tuple]: 验证结果列表
    """
    shots = getattr(model, 'shots', [])
    model_version = getattr(model, 'model_version', 'seedance-2.5')

    if not shots:
        return [(Severity.OK, "无镜头数据，跳过时长检查")]

    # 获取模型时长约束
    caps = MODEL_CAPS.get(model_version, MODEL_CAPS["seedance-2.5"])
    max_dur = caps["max"]
    min_dur = caps["min"]

    violations = []

    for shot in shots:
        shot_id = shot.get('id', '?')
        duration = shot.get('duration', 0)

        if duration > max_dur:
            violations.append(f"{shot_id}={duration}s(超{max_dur}s上限)")
        elif duration < min_dur:
            violations.append(f"{shot_id}={duration}s(低于{min_dur}s下限)")

    if violations:
        return [(
            Severity.FAIL,
            f"时长违规: {', '.join(violations)} → 调整到 {min_dur}-{max_dur}s"
        )]
    else:
        return [(Severity.OK, f"时长全合规({len(shots)}个镜头, {min_dur}-{max_dur}s)")]


# 创建规则卡片
rule_deliver_envelope = technical_rule(
    id="R026",
    name="逐镜交付包络",
    rule=check_deliver_envelope,
    validate=lambda output: output,
    description="检查每个镜头是否符合 per-model 秒数上限",
    examples=[
        '✅ 2.5 模型，镜头 25s → 通过',
        '❌ 2.5 模型，镜头 32s → FAIL',
        '❌ 2.5 模型，镜头 2s → FAIL'
    ],
    rationale="超上限 API 直接拒绝，低于下限质量差",
    references=["AiFilm-pipeline/code/validators.py:_g14_deliver_envelope"],
    priority=90,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("逐镜交付包络规则测试")
    print("=" * 60)

    # 测试1: 合规
    class PassModel:
        model_version = "seedance-2.5"
        shots = [
            {'id': 'SH01', 'duration': 10},
            {'id': 'SH02', 'duration': 25},
        ]

    result = rule_deliver_envelope.apply(PassModel())
    print(f"\n测试1 - 合规:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 超上限
    class FailModel1:
        model_version = "seedance-2.5"
        shots = [
            {'id': 'SH01', 'duration': 32},
        ]

    result = rule_deliver_envelope.apply(FailModel1())
    print(f"\n测试2 - 超上限:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 低于下限
    class FailModel2:
        model_version = "seedance-2.5"
        shots = [
            {'id': 'SH01', 'duration': 2},
        ]

    result = rule_deliver_envelope.apply(FailModel2())
    print(f"\n测试3 - 低于下限:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
