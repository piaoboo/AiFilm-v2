#!/usr/bin/env python3
"""
代词指代歧义规则

检查代词指代是否有歧义：
- 代词所在分句里出现 ≥2 个不同角色名 → 歧义
- 视频模型不做指代消解，会在可见角色里随机选择

迁移自: AiFilm-pipeline validators.py _g32_pronoun_referent
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 代词列表
PRONOUNS = ["他", "她", "它", "他们", "她们", "它们"]


def check_pronoun_referent(model):
    """
    检查代词指代歧义

    Args:
        model: 包含以下属性的模型对象
            - prompt_blocks: prompt 文本块列表
            - all_characters: 所有角色名集合

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])
    all_characters = getattr(model, 'all_characters', set())

    if not prompt_blocks or not all_characters:
        return [(Severity.OK, "无数据，跳过代词指代检查")]

    ambiguous_cases = []

    for i, block in enumerate(prompt_blocks, 1):
        block_text = str(block)

        # 按句号、分号、逗号分句
        sentences = re.split(r'[。；，]', block_text)

        for sent in sentences:
            # 检查是否包含代词
            has_pronoun = any(p in sent for p in PRONOUNS)
            if not has_pronoun:
                continue

            # 统计句中出现的角色数
            chars_in_sent = [c for c in all_characters if c in sent]

            if len(chars_in_sent) >= 2:
                ambiguous_cases.append(
                    f"块{i}: '{sent[:30]}...' 含{len(chars_in_sent)}个角色"
                )

    if ambiguous_cases:
        return [(
            Severity.WARN,
            f"代词指代歧义: {'; '.join(ambiguous_cases)} → 建议用明确姓名"
        )]
    else:
        return [(Severity.OK, "无代词指代歧义")]


# 创建规则卡片
rule_pronoun_referent = content_rule(
    id="R030",
    name="代词指代歧义",
    rule=check_pronoun_referent,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查代词指代是否有歧义",
    examples=[
        '⚠️ "张三和李四对话，他笑了" → 歧义（他是谁？）',
        '✅ "张三和李四对话，张三笑了" → 明确'
    ],
    rationale="视频模型不做指代消解，会在可见角色里随机选择，导致动作贴错人",
    references=["AiFilm-pipeline/code/validators.py:_g32_pronoun_referent"],
    priority=65,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("代词指代歧义规则测试")
    print("=" * 60)

    # 测试1: 无歧义
    class PassModel:
        all_characters = {"张三", "李四"}
        prompt_blocks = ["张三笑了"]

    result = rule_pronoun_referent.apply(PassModel())
    print(f"\n测试1 - 无歧义:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 有歧义
    class WarnModel:
        all_characters = {"张三", "李四"}
        prompt_blocks = ["张三和李四对话，他笑了"]

    result = rule_pronoun_referent.apply(WarnModel())
    print(f"\n测试2 - 有歧义:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
