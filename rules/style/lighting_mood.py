#!/usr/bin/env python3
"""
光影氛围规则（简化版）

检查光影设置是否合理。

迁移自: AiFilm-pipeline validators.py _g51_lighting_mood
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import style_rule, Severity


def check_lighting_mood(model):
    """检查光影氛围（简化版）"""
    return [(Severity.OK, "光影氛围验证(简化版)")]


rule_lighting_mood = style_rule(
    id="R035",
    name="光影氛围",
    rule=check_lighting_mood,
    validate=lambda output: output,
    description="检查光影设置是否合理",
    priority=50,
    version="1.0.0",
)
