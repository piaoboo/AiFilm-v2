#!/usr/bin/env python3
"""
时长约束规则

验证单镜时长在合理范围内

迁移自: AiFilm-pipeline validators.py _g11_episode_dur
版本: v1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity, AppliesTo

def check_duration(model):
    """检查时长约束"""
    duration = getattr(model, 'duration', 0)

    if duration <= 0:
        return [(Severity.FAIL, "时长必须大于0")]

    # Seedance 限制 30s
    if getattr(model, 'is_seedance', False) and duration > 30:
        return [(Severity.FAIL, f"Seedance 单镜时长{duration}s超过30s上限")]

    # H3 限制 4-15s
    if getattr(model, 'is_h3', False):
        if duration < 4 or duration > 15:
            return [(Severity.FAIL, f"H3 时长{duration}s必须在4-15s范围内")]

    return [(Severity.OK, f"时长{duration}s合理")]

rule_duration = technical_rule(
    id="R007",
    name="时长约束",
    rule=check_duration,
    validate=lambda output: output,
    description="验证单镜时长在合理范围内（Seedance≤30s, H3=4-15s）",
    priority=85,
    version="1.0.0",
)
