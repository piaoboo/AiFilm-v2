#!/usr/bin/env python3
"""
反陈词滥调规则

检查全文是否含反口水词（空洞形容词/副词）：
- 中文: 氛围感 / 质感 / 层次感 / 沉浸感 等
- 英文: cinematic / epic / stunning / masterpiece 等

迁移自: AiFilm-pipeline validators.py _g04_anticliche
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 中文口水词列表
ANTI_CLICHE_ZH = [
    "氛围感", "质感", "层次感", "沉浸感",
    "电影感", "史诗感", "震撼感", "张力感",
    "高级感", "神秘感", "仪式感", "情绪感",
]

# 英文口水词列表（需要词边界检查）
ANTI_CLICHE_EN = [
    "cinematic", "epic", "stunning", "masterpiece",
    "breathtaking", "dramatic", "intense", "powerful",
    "beautiful", "gorgeous", "amazing", "incredible",
]


def check_anticliche(model):
    """
    检查反陈词滥调

    Args:
        model: 包含 full_text 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    full_text = getattr(model, 'full_text', '')

    if not full_text:
        # 尝试从 prompt_blocks 构建
        prompt_blocks = getattr(model, 'prompt_blocks', [])
        full_text = '\n'.join(str(block) for block in prompt_blocks)

    hits = []

    # 检查中文口水词
    for word in ANTI_CLICHE_ZH:
        if word in full_text:
            hits.append(word)

    # 检查英文口水词（使用词边界）
    for word in ANTI_CLICHE_EN:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, full_text, re.IGNORECASE):
            hits.append(word)

    if hits:
        return [(
            Severity.FAIL,
            "反口水词命中: " + ", ".join(hits) + " → 替换为具体视觉描述"
        )]
    else:
        return [(Severity.OK, "无口水词")]


# 创建规则卡片
rule_anticliche = content_rule(
    id="R011",
    name="反陈词滥调",
    rule=check_anticliche,
    validate=lambda output: output,
    severity=Severity.FAIL,
    description="检查全文是否含反口水词（空洞形容词/副词），必须用具体视觉描述替换",
    examples=[
        '✅ "暖色调的昏黄灯光，透过烟雾形成柔和光束"',
        '❌ "充满电影感的氛围" → FAIL'
    ],
    rationale="口水词是抽象标签，模型无法理解，必须用具体视觉描述替换",
    references=["AiFilm-pipeline/code/validators.py:_g04_anticliche"],
    priority=85,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("反陈词滥调规则测试")
    print("=" * 60)

    # 测试1: 无口水词
    class PassModel:
        full_text = "暖色调的昏黄灯光，透过烟雾形成柔和光束"

    result = rule_anticliche.apply(PassModel())
    print(f"\n测试1 - 无口水词:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 中文口水词
    class FailModelZH:
        full_text = "充满电影感的氛围，营造出质感"

    result = rule_anticliche.apply(FailModelZH())
    print(f"\n测试2 - 中文口水词:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 英文口水词
    class FailModelEN:
        full_text = "A cinematic and epic scene with stunning visuals"

    result = rule_anticliche.apply(FailModelEN())
    print(f"\n测试3 - 英文口水词:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
