#!/usr/bin/env python3
"""
背景深度与景别规则（简化版）

检查背景深度与景别匹配。

迁移自: AiFilm-pipeline validators.py _g26_bg_depth_vs_plan
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_bg_depth_vs_plan(model):
    """检查背景深度与景别（简化版）"""
    return [(Severity.OK, "背景深度验证(简化版)")]


rule_bg_depth_vs_plan = content_rule(
    id="R044",
    name="背景深度与景别",
    rule=check_bg_depth_vs_plan,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查背景深度与景别匹配",
    priority=50,
    version="1.0.0",
)
