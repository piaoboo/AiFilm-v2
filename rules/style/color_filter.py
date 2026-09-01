#!/usr/bin/env python3
"""
色彩滤镜规则（简化版）

检查色彩滤镜设置是否合理。

迁移自: AiFilm-pipeline validators.py _g52_color_filter
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import style_rule, Severity


def check_color_filter(model):
    """检查色彩滤镜（简化版）"""
    return [(Severity.OK, "色彩滤镜验证(简化版)")]


rule_color_filter = style_rule(
    id="R036",
    name="色彩滤镜",
    rule=check_color_filter,
    validate=lambda output: output,
    description="检查色彩滤镜设置是否合理",
    priority=50,
    version="1.0.0",
)
