#!/usr/bin/env python3
"""
H3模式路由规则

验证H3模式路由的一致性

迁移自: AiFilm-pipeline code/gate_46_h3_routing.py
版本: v1.0.0
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import h3_rule, Severity

def check_h3_routing(model):
    """检查H3模式路由"""
    h3_mode = getattr(model, 'h3_mode', None)

    if not h3_mode:
        return [(Severity.OK, "非H3项目，跳过检查")]

    H3_MODES = ["t2va", "i2va", "l2va", "fl2va", "ref2va"]

    if h3_mode not in H3_MODES:
        return [(Severity.FAIL, f"无效的h3_mode: {h3_mode}")]

    # 检查模式与资源一致性
    if h3_mode == 'i2va':
        if not getattr(model, 'blocking_keyframe', None):
            return [(Severity.FAIL, "i2va模式缺少blocking_keyframe")]

    elif h3_mode == 'ref2va':
        if not getattr(model, 'asset_images', None):
            return [(Severity.FAIL, "ref2va模式缺少asset_images")]

    return [(Severity.OK, f"H3模式路由({h3_mode})正确")]

rule_h3_routing = h3_rule(
    id="R009",
    name="H3模式路由",
    rule=check_h3_routing,
    validate=lambda output: output,
    description="验证H3模式路由的一致性",
    priority=90,
    version="1.0.0",
)
