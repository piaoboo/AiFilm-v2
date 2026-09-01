#!/usr/bin/env python3
"""
五等式结构规则

检查五个计数是否严格相等：
子单元数 = 故事板数 = 视频prompt数 = Style数 = 锚定数

迁移自: AiFilm-pipeline validators.py _g01_five_eq
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import structure_rule, Severity


def check_five_equations(model):
    """
    检查五等式是否相等

    Args:
        model: 包含以下属性的模型对象
            - n_sub: 子单元数
            - n_sb: 故事板数
            - n_vid: 视频prompt数
            - n_sty: Style数
            - n_anc: 锚定数

    Returns:
        List[tuple]: 验证结果列表 [(severity, message), ...]
    """
    counts = (
        getattr(model, 'n_sub', 0),
        getattr(model, 'n_sb', 0),
        getattr(model, 'n_vid', 0),
        getattr(model, 'n_sty', 0),
        getattr(model, 'n_anc', 0),
    )

    n_sub, n_sb, n_vid, n_sty, n_anc = counts

    # 检查是否所有计数相等且大于0
    if len(set(counts)) == 1 and n_sub > 0:
        return [(
            Severity.OK,
            f"五等式齐 (子单元=故事板=视频prompt=Style=锚定={n_sub})"
        )]
    else:
        return [(
            Severity.FAIL,
            f"五等式不齐 子单元={n_sub} 故事板={n_sb} 视频prompt={n_vid} "
            f"Style={n_sty} 锚定={n_anc} → 静默数据丢失,回 F3/Q3"
        )]


# 创建规则卡片
rule_five_equations = structure_rule(
    id="R001",
    name="五等式结构",
    rule=check_five_equations,
    validate=lambda output: output,  # 规则本身返回验证结果
    description="检查五个计数是否严格相等: 子单元数 = 故事板数 = 视频prompt数 = Style数 = 锚定数",
    examples=[
        "✅ 子单元=5, 故事板=5, prompt=5, Style=5, 锚定=5",
        "❌ 子单元=5, 故事板=4 → FAIL '静默数据丢失,回 F3/Q3'"
    ],
    rationale="不齐意味着某个环节数据丢失，会导致渲染错误",
    references=["AiFilm-pipeline/code/validators.py:_g01_five_eq"],
    priority=100,  # 最高优先级
    version="1.0.0",
)


if __name__ == "__main__":
    # 测试规则
    print("=" * 60)
    print("五等式结构规则测试")
    print("=" * 60)

    # 测试用例1: 五等式齐
    class PassModel:
        n_sub = 5
        n_sb = 5
        n_vid = 5
        n_sty = 5
        n_anc = 5

    result = rule_five_equations.apply(PassModel())
    print(f"\n测试1 - 五等式齐:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试用例2: 五等式不齐
    class FailModel:
        n_sub = 5
        n_sb = 4
        n_vid = 5
        n_sty = 5
        n_anc = 5

    result = rule_five_equations.apply(FailModel())
    print(f"\n测试2 - 五等式不齐:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试用例3: 全零
    class ZeroModel:
        n_sub = 0
        n_sb = 0
        n_vid = 0
        n_sty = 0
        n_anc = 0

    result = rule_five_equations.apply(ZeroModel())
    print(f"\n测试3 - 全零:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
