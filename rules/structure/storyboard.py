#!/usr/bin/env python3
"""
故事板完整性规则

检查故事板格式是否正确：
- 每条故事板必须包含镜号引用「镜N」
- 必须是分镜格式，非英文梗概

迁移自: AiFilm-pipeline validators.py _g17_storyboard
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import structure_rule, Severity

# 镜号正则
SHOT_NO_RE = re.compile(r'镜\d+')


def check_storyboard(model):
    """
    检查故事板完整性

    Args:
        model: 包含 storyboard 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    storyboard = getattr(model, 'storyboard', None)

    if not storyboard:
        return [(Severity.OK, "故事板格式闸跳过:无结构化 storyboard")]

    # 检查每条故事板是否包含镜号
    bad_sb = []
    for gid, txt in sorted(storyboard.items(), key=lambda kv: str(kv[0])):
        if not SHOT_NO_RE.search(str(txt)):
            bad_sb.append(str(gid))

    if bad_sb:
        return [(
            Severity.FAIL,
            f"故事板非分镜格式(无镜号引用): 子单元{', '.join(bad_sb)} "
            f"→ 须写「镜N | 景别运镜 — 描述」逐镜分镜(非英文/散文梗概)"
        )]
    else:
        return [(Severity.OK, f"故事板格式正确({len(storyboard)}条)")]


# 创建规则卡片
rule_storyboard = structure_rule(
    id="R012",
    name="故事板完整性",
    rule=check_storyboard,
    validate=lambda output: output,
    description="检查故事板格式是否正确：每条必须包含镜号引用",
    examples=[
        '✅ "镜1 | 中景 — 侦探推开车门"',
        '❌ "Girl slaps man. 9:16." → FAIL (无镜号)'
    ],
    rationale="故事板是分镜的可视化表示，必须是正确的分镜格式",
    references=["AiFilm-pipeline/code/validators.py:_g17_storyboard"],
    priority=80,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("故事板完整性规则测试")
    print("=" * 60)

    # 测试1: 正确格式
    class PassModel:
        storyboard = {
            1: "镜1 | 中景 — 侦探推开车门",
            2: "镜2 | 特写 — 侦探拿出手机",
        }

    result = rule_storyboard.apply(PassModel())
    print(f"\n测试1 - 正确格式:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 缺少镜号
    class FailModel:
        storyboard = {
            1: "镜1 | 中景 — 侦探推开车门",
            2: "Girl slaps man. 9:16.",
        }

    result = rule_storyboard.apply(FailModel())
    print(f"\n测试2 - 缺少镜号:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
