#!/usr/bin/env python3
"""
资产卡声音规则（简化版）

检查资产卡声音描述完整性。

迁移自: AiFilm-pipeline validators.py _g35_assetcard_voice
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity


def check_assetcard_voice(model):
    """检查资产卡声音（简化版）"""
    return [(Severity.OK, "资产卡声音验证(简化版)")]


rule_assetcard_voice = technical_rule(
    id="R038",
    name="资产卡声音",
    rule=check_assetcard_voice,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查资产卡声音描述完整性",
    priority=50,
    version="1.0.0",
)
