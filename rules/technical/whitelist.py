#!/usr/bin/env python3
"""
防串台白名单规则

检查角色/场景/道具是否在资产卡白名单中：
- 所有出现的资产必须预先在白名单注册
- 防止跨项目串台（模型记忆污染）

迁移自: AiFilm-pipeline validators.py _g09_whitelist
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import technical_rule, Severity


def split_names(text):
    """分割名称列表（支持全半角逗号和顿号）"""
    # 分隔符：全角逗号、半角逗号、顿号
    names = re.split(r'[，,、]', text)
    return [n.strip() for n in names if n.strip()]


def check_whitelist(model):
    """
    检查白名单

    Args:
        model: 包含以下属性的模型对象
            - declared_chars: 声明的角色列表
            - whitelist: 白名单集合（或从 assetcard 读取）
            - assetcard: 资产卡路径（可选）

    Returns:
        List[tuple]: 验证结果列表
    """
    declared_chars = getattr(model, 'declared_chars', [])
    whitelist = getattr(model, 'whitelist', None)
    assetcard_path = getattr(model, 'assetcard', None)

    # 如果有资产卡路径，尝试读取白名单
    if assetcard_path and not whitelist:
        try:
            with open(assetcard_path, encoding='utf-8') as f:
                ac = f.read()
            match = re.search(r"人名[：:]\s*(.+)", ac)
            if match:
                whitelist = set(split_names(match.group(1)))
        except Exception:
            pass

    # 如果没有白名单，跳过检查
    if not whitelist:
        return [(Severity.WARN, "资产卡 §G 未找到人名白名单 → 跳过防串台校验")]

    # 检查未注册的角色
    unregistered = [char for char in declared_chars if char not in whitelist]

    if unregistered:
        return [(
            Severity.FAIL,
            f"未注册角色: {', '.join(unregistered)} → 须在资产卡 §G 注册"
        )]
    else:
        return [(Severity.OK, f"角色白名单全过({len(declared_chars)}个角色)")]


# 创建规则卡片
rule_whitelist = technical_rule(
    id="R014",
    name="防串台白名单",
    rule=check_whitelist,
    validate=lambda output: output,
    description="检查角色/场景/道具是否在资产卡白名单中",
    examples=[
        '✅ prompt 含 "张三"，白名单有 "张三"',
        '❌ prompt 含 "李四"，白名单没有 "李四" → FAIL'
    ],
    rationale="未注册资产可能是其他项目的角色，导致风格/外观串台",
    references=["AiFilm-pipeline/code/validators.py:_g09_whitelist"],
    priority=75,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("防串台白名单规则测试")
    print("=" * 60)

    # 测试1: 全部注册
    class PassModel:
        declared_chars = ["张三", "李四"]
        whitelist = {"张三", "李四", "王五"}

    result = rule_whitelist.apply(PassModel())
    print(f"\n测试1 - 全部注册:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 未注册角色
    class FailModel:
        declared_chars = ["张三", "赵六"]
        whitelist = {"张三", "李四"}

    result = rule_whitelist.apply(FailModel())
    print(f"\n测试2 - 未注册角色:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 无白名单
    class NoWhitelistModel:
        declared_chars = ["张三"]

    result = rule_whitelist.apply(NoWhitelistModel())
    print(f"\n测试3 - 无白名单:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
