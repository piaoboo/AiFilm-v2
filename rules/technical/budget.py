#!/usr/bin/env python3
"""
预算管理规则

验证字数预算不超限

迁移自: AiFilm-pipeline validators.py _g10_zh_budget
版本: v1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, RuleCategory, Severity

def check_budget(model):
    """检查字数预算"""
    zh_budget = getattr(model, 'zh_budget', 0)
    zh_used = getattr(model, 'zh_used', 0)

    if zh_budget > 0 and zh_used > zh_budget:
        return [(Severity.WARN, f"字数超预算: {zh_used}/{zh_budget}")]

    return [(Severity.OK, f"字数预算正常: {zh_used}/{zh_budget}")]

rule_budget = RuleCard(
    id="R008",
    name="预算管理",
    category=RuleCategory.TECHNICAL,
    rule=check_budget,
    validate=lambda output: output,
    severity=Severity.WARN,  # 预算是软闸
    description="验证字数预算不超限",
    priority=50,
    version="1.0.0",
)
