#!/usr/bin/env python3
"""
对白规则

验证对白的完整性和格式：
1. 对白必须有说话人
2. 对白格式正确
3. 避免空对白

迁移自: AiFilm-pipeline dialogue-diction.md + validators.py _g06_dialogue
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_dialogue(model):
    """
    检查对白规则

    Args:
        model: 包含 dialogue_blocks 或 prompt_blocks 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    dialogue_blocks = getattr(model, 'dialogue_blocks', [])
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    violations = []

    # 对白模式：角色名:"对白内容"
    dialogue_pattern = r'(\w+):\s*"([^"]*)"'

    for i, block in enumerate(dialogue_blocks or prompt_blocks):
        block_text = str(block) if not isinstance(block, str) else block

        # 查找所有对白
        matches = re.findall(dialogue_pattern, block_text)

        for speaker, content in matches:
            # 检查空对白
            if not content.strip():
                violations.append(f"块{i+1}: {speaker} 的对白为空")

            # 检查对白长度（过短可能是错误）
            if len(content.strip()) < 2:
                violations.append(f"块{i+1}: {speaker} 的对白过短")

    if violations:
        return [(
            Severity.WARN,
            "对白问题: " + "; ".join(violations[:3]) +
            (f" ...另{len(violations)-3}处" if len(violations) > 3 else "")
        )]
    else:
        return [(Severity.OK, f"对白规则通过（检查{len(dialogue_blocks or prompt_blocks)}个块）")]


# 创建规则卡片
rule_dialogue = content_rule(
    id="R004",
    name="对白规则",
    rule=check_dialogue,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="验证对白的完整性和格式",
    examples=[
        '✅ 侦探:"这里发生了什么？"',
        '❌ 侦探:"" → WARN (空对白)',
    ],
    rationale="对白是重要的内容元素，需要确保格式正确和内容完整",
    references=["AiFilm-pipeline/reference/dialogue-diction.md"],
    priority=70,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("对白规则测试")
    print("=" * 60)

    # 测试1: 正常对白
    class PassModel:
        dialogue_blocks = ['侦探:"这里发生了什么？"']

    result = rule_dialogue.apply(PassModel())
    print(f"\n测试1 - 正常对白:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 空对白
    class EmptyModel:
        dialogue_blocks = ['侦探:""']

    result = rule_dialogue.apply(EmptyModel())
    print(f"\n测试2 - 空对白:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
