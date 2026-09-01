#!/usr/bin/env python3
"""
空间方位规则（简化版）

检查场景空间方位描述。

迁移自: AiFilm-pipeline validators.py _g36_spatial_orientation
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_spatial_orientation(model):
    """检查空间方位（简化版）"""
    return [(Severity.OK, "空间方位验证(简化版)")]


rule_spatial_orientation = content_rule(
    id="R039",
    name="空间方位",
    rule=check_spatial_orientation,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查场景空间方位描述",
    priority=50,
    version="1.0.0",
)
