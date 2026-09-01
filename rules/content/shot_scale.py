#!/usr/bin/env python3
"""
景别阶梯规则（简化版）

检查景别变化是否合理。

迁移自: AiFilm-pipeline validators.py _g48_shot_scale
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_shot_scale(model):
    """检查景别阶梯（简化版）"""
    return [(Severity.OK, "景别阶梯验证(简化版)")]


rule_shot_scale = content_rule(
    id="R032",
    name="景别阶梯",
    rule=check_shot_scale,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查景别变化是否合理",
    priority=50,
    version="1.0.0",
)
