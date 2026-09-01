#!/usr/bin/env python3
"""
跨模型词汇泄漏规则

检查 H3 专用词汇是否泄漏到 Seedance 项目：
- H3 Context-IR 字段名（行首锚定）
- H3 台词标记 <d>

迁移自: AiFilm-pipeline validators.py _g41_foreign_h3_vocab
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import h3_rule, Severity

# H3 专用字段（行首锚定）
FOREIGN_H3_FIELDS = [
    "summary",
    "detailed_description",
    "camera_movement",
    "lighting",
    "style",
    "context",
]

# H3 台词标记
H3_DIALOGUE_MARKER = "<d>"


def check_foreign_h3_vocab(model):
    """
    检查跨模型词汇泄漏

    Args:
        model: 包含以下属性的模型对象
            - prompt_blocks: prompt 文本块列表
            - is_h3: 是否为 H3 项目

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    is_h3 = getattr(model, 'is_h3', False)

    if not prompt_blocks:
        return [(Severity.OK, "跨模型词汇闸跳过:无 prompt_blocks")]

    # H3 项目不检查
    if is_h3:
        return [(Severity.OK, "H3 项目跳过外来词检查")]

    violations = []

    # 检查字段名（行首锚定）
    field_pattern = re.compile(r'^\s*(' + '|'.join(FOREIGN_H3_FIELDS) + r')\s*:', re.MULTILINE)

    for i, block in enumerate(prompt_blocks, 1):
        block_text = str(block)

        # 检查字段名
        field_matches = field_pattern.findall(block_text)
        if field_matches:
            violations.append(f"块{i}含H3字段: {', '.join(set(field_matches))}")

        # 检查台词标记
        if H3_DIALOGUE_MARKER in block_text:
            violations.append(f"块{i}含<d>标记")

    if violations:
        return [(
            Severity.FAIL,
            f"跨模型词汇泄漏: {'; '.join(violations)} → 移除 H3 专用语法"
        )]
    else:
        return [(Severity.OK, f"无跨模型词汇泄漏({len(prompt_blocks)}个块)")]


# 创建规则卡片
rule_foreign_h3_vocab = h3_rule(
    id="R025",
    name="跨模型词汇泄漏",
    rule=check_foreign_h3_vocab,
    validate=lambda output: output,
    severity=Severity.FAIL,
    description="检查 H3 专用词汇是否泄漏到 Seedance 项目",
    examples=[
        '❌ prompt 含 "summary:" 字段 → FAIL',
        '❌ prompt 含 "<d>" 标记 → FAIL',
        '✅ 无 H3 专用语法'
    ],
    rationale="两轨并跑时容易写串，H3 语法在 Seedance 中无效",
    references=["AiFilm-pipeline/code/validators.py:_g41_foreign_h3_vocab"],
    priority=80,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("跨模型词汇泄漏规则测试")
    print("=" * 60)

    # 测试1: 无泄漏
    class PassModel:
        is_h3 = False
        prompt_blocks = ["Dynamic: 角色动作描述"]

    result = rule_foreign_h3_vocab.apply(PassModel())
    print(f"\n测试1 - 无泄漏:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: H3 字段泄漏
    class FailModel1:
        is_h3 = False
        prompt_blocks = ["summary: 场景描述\nDynamic: 动作"]

    result = rule_foreign_h3_vocab.apply(FailModel1())
    print(f"\n测试2 - H3 字段泄漏:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: H3 标记泄漏
    class FailModel2:
        is_h3 = False
        prompt_blocks = ["Dynamic: <d>对话内容</d>"]

    result = rule_foreign_h3_vocab.apply(FailModel2())
    print(f"\n测试3 - H3 标记泄漏:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
