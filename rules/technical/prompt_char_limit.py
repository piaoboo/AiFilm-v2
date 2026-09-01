#!/usr/bin/env python3
"""
prompt 字符长度接近上限规则

检查 prompt 总字符数是否接近 15,000 上限：
- API 上限: 15,000 字符
- WARN 阈值: 13,500 字符（90%）
- CRITICAL 阈值: 14,500 字符（96.7%）

迁移自: AiFilm-pipeline validators.py _g39_prompt_char_limit
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory

# prompt 字符限制
PROMPT_CHAR_LIMIT = 15000
WARN_THRESHOLD = int(PROMPT_CHAR_LIMIT * 0.9)  # 90%
CRITICAL_THRESHOLD = int(PROMPT_CHAR_LIMIT * 0.967)  # 96.7%


def check_prompt_char_limit(model):
    """
    检查 prompt 字符长度

    Args:
        model: 包含 prompt_blocks 或 full_text 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    full_text = getattr(model, 'full_text', '')

    # 计算总字符数
    if prompt_blocks:
        total_chars = sum(len(str(block)) for block in prompt_blocks)
    elif full_text:
        total_chars = len(full_text)
    else:
        return [(Severity.OK, "无 prompt 数据，跳过字符限制检查")]

    percentage = (total_chars / PROMPT_CHAR_LIMIT) * 100

    if total_chars >= CRITICAL_THRESHOLD:
        return [(
            Severity.WARN,
            f"🔴 prompt 字符严重接近上限: {total_chars}/{PROMPT_CHAR_LIMIT} ({percentage:.1f}%) "
            f"→ 超过 {PROMPT_CHAR_LIMIT} 会被截断"
        )]
    elif total_chars >= WARN_THRESHOLD:
        return [(
            Severity.WARN,
            f"⚠️ prompt 字符接近上限: {total_chars}/{PROMPT_CHAR_LIMIT} ({percentage:.1f}%) "
            f"→ 建议精简"
        )]
    else:
        return [(Severity.OK, f"prompt 字符数正常: {total_chars}/{PROMPT_CHAR_LIMIT} ({percentage:.1f}%)")]


# 创建规则卡片
rule_prompt_char_limit = RuleCard(
    id="R029",
    name="prompt 字符长度限制",
    category=RuleCategory.TECHNICAL,
    rule=check_prompt_char_limit,
    severity=Severity.WARN,
    description="检查 prompt 总字符数是否接近 15,000 上限",
    examples=[
        '✅ prompt 5,000 字符（正常）',
        '⚠️ prompt 13,800 字符（90%）→ WARN',
        '🔴 prompt 14,800 字符（98%）→ WARN'
    ],
    rationale="超过 15,000 字符会被 API 截断，导致后半部分指令丢失",
    references=["AiFilm-pipeline/code/validators.py:_g39_prompt_char_limit"],
    priority=85,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("prompt 字符长度限制规则测试")
    print("=" * 60)

    # 测试1: 正常
    class PassModel:
        full_text = "A" * 5000

    result = rule_prompt_char_limit.apply(PassModel())
    print(f"\n测试1 - 正常:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 接近上限
    class WarnModel1:
        full_text = "A" * 13800

    result = rule_prompt_char_limit.apply(WarnModel1())
    print(f"\n测试2 - 接近上限:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 严重接近上限
    class WarnModel2:
        full_text = "A" * 14800

    result = rule_prompt_char_limit.apply(WarnModel2())
    print(f"\n测试3 - 严重接近上限:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
