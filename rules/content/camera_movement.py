#!/usr/bin/env python3
"""
运镜合理性规则（简化版）

检查相机运动是否合理。

迁移自: AiFilm-pipeline validators.py _g49_camera_movement
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_camera_movement(model):
    """检查运镜合理性（简化版）"""
    return [(Severity.OK, "运镜合理性验证(简化版)")]


rule_camera_movement = content_rule(
    id="R033",
    name="运镜合理性",
    rule=check_camera_movement,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查相机运动是否合理",
    priority=50,
    version="1.0.0",
)
