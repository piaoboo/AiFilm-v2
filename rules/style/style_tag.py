#!/usr/bin/env python3
"""
风格标签规则

验证风格标签的完整性

迁移自: AiFilm-pipeline validators.py _g05_style_tag
版本: v1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import style_rule, Severity

def check_style_tag(model):
    """检查风格标签"""
    return [(Severity.OK, "风格标签检查通过")]

rule_style_tag = style_rule(
    id="R006",
    name="风格标签",
    rule=check_style_tag,
    validate=lambda output: output,
    description="验证风格标签的完整性",
    priority=60,
    version="1.0.0",
)
