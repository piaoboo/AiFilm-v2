#!/usr/bin/env python3
"""
站位承重规则

计算多人戏的站位承重，用于H3模式选择

迁移自: AiFilm-pipeline code/h3_adapter.py
版本: v1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import h3_rule, Severity

def check_positioning_weight(model):
    """检查站位承重"""
    characters = getattr(model, 'characters', [])

    if not characters:
        return [(Severity.OK, "无角色，跳过检查")]

    # 简化的站位承重计算
    char_count = len(characters)
    positioning_weight = min(char_count * 2, 10)

    # 提供模式建议
    if positioning_weight >= 7:
        suggestion = "建议使用 i2va (站位承重高)"
    elif positioning_weight >= 4:
        suggestion = "可使用 i2va 或 ref2va"
    else:
        suggestion = "建议使用 ref2va (站位承重低)"

    return [(Severity.OK, f"站位承重={positioning_weight}, {suggestion}")]

rule_positioning_weight = h3_rule(
    id="R010",
    name="站位承重",
    rule=check_positioning_weight,
    validate=lambda output: output,
    severity=Severity.OK,
    description="计算多人戏的站位承重，用于H3模式选择",
    priority=85,
    version="1.0.0",
)
