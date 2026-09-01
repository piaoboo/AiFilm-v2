#!/usr/bin/env python3
"""
字幕安全区规则

检查竖屏（9:16）字幕是否在安全区内：
- 9:16 竖屏: 字幕需要避开底部 UI 热区
- 16:9 横屏: 标准安全区（跳过检查）

迁移自: AiFilm-pipeline validators.py _g19_subtitle_safezone
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity

# 安全区措辞 token
SAFE_ZONE_TOKENS = [
    "字幕区", "头顶留白", "上半区", "中上区域",
    "避开底部", "预留字幕", "字幕安全区"
]


def check_subtitle_safezone(model):
    """
    检查字幕安全区

    Args:
        model: 包含 prompt_blocks 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    prompt_blocks = getattr(model, 'prompt_blocks', [])

    if not prompt_blocks:
        return [(Severity.OK, "无 prompt 块，跳过字幕安全区检查")]

    n_vert = 0
    missing = []

    for i, blk in enumerate(prompt_blocks, 1):
        # 检查画幅比例
        match = re.search(r"(\d+)\s*[:：]\s*(\d+)", str(blk))
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            # 竖屏判定
            if height > width:
                n_vert += 1
                # 检查是否包含安全区措辞
                has_token = any(token in str(blk) for token in SAFE_ZONE_TOKENS)
                if not has_token:
                    missing.append(f"块{i}")

    if n_vert == 0:
        return [(Severity.OK, "无竖屏镜头，跳过字幕安全区检查")]

    if missing:
        return [(
            Severity.WARN,
            f"竖屏镜头缺字幕安全区措辞: {', '.join(missing)} "
            f"→ 建议添加'字幕区'/'上半区'等措辞"
        )]
    else:
        return [(Severity.OK, f"竖屏字幕安全区全覆盖({n_vert}个竖屏镜头)")]


# 创建规则卡片
rule_subtitle_safezone = content_rule(
    id="R019",
    name="字幕安全区",
    rule=check_subtitle_safezone,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查竖屏（9:16）字幕是否在安全区内",
    examples=[
        '✅ 竖屏 prompt 含"字幕区"或"上半区"',
        '⚠️ 竖屏 prompt 缺安全区措辞 → WARN'
    ],
    rationale="移动端 UI 会遮挡底部字幕，需要预留安全区",
    references=["AiFilm-pipeline/code/validators.py:_g19_subtitle_safezone"],
    priority=60,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("字幕安全区规则测试")
    print("=" * 60)

    # 测试1: 竖屏有安全区措辞
    class PassModel:
        prompt_blocks = [
            "镜1，5秒。9:16。画面上半区留白，避开底部字幕区",
        ]

    result = rule_subtitle_safezone.apply(PassModel())
    print(f"\n测试1 - 有安全区措辞:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 竖屏缺安全区措辞
    class WarnModel:
        prompt_blocks = [
            "镜1，5秒。9:16。人物站立",
        ]

    result = rule_subtitle_safezone.apply(WarnModel())
    print(f"\n测试2 - 缺安全区措辞:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试3: 横屏
    class HorizontalModel:
        prompt_blocks = [
            "镜1，5秒。16:9。横屏场景",
        ]

    result = rule_subtitle_safezone.apply(HorizontalModel())
    print(f"\n测试3 - 横屏:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
