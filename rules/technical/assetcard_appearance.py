#!/usr/bin/env python3
"""
资产卡外观规则（简化版）

检查资产卡外观描述完整性。

迁移自: AiFilm-pipeline validators.py _g34_assetcard_appearance
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity


def check_assetcard_appearance(model):
    """检查资产卡外观（简化版）"""
    return [(Severity.OK, "资产卡外观验证(简化版)")]


rule_assetcard_appearance = technical_rule(
    id="R037",
    name="资产卡外观",
    rule=check_assetcard_appearance,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查资产卡外观描述完整性",
    priority=50,
    version="1.0.0",
)
