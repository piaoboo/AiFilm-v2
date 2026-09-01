#!/usr/bin/env python3
"""
版权署名规则

检查视听签名块的8字段完整性：
- 项目名
- 作者
- 许可证
- 等其他必需字段

迁移自: AiFilm-pipeline validators.py _g13_signature
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory

# 签名必需字段
SIGNATURE_FIELDS = [
    "project_name",
    "author",
    "license",
    "genre",
    "style",
    "mood",
    "camera_emotion",
    "director_dna",
]


def check_signature(model):
    """
    检查版权署名

    Args:
        model: 包含 signature 的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    signature = getattr(model, 'signature', None)

    if signature is None:
        return [(
            Severity.WARN,
            "视听签名块缺失:无 SIGNATURE(8字段) → 旧集宽容,新集应补"
        )]

    if not isinstance(signature, dict):
        return [(
            Severity.FAIL,
            f"视听签名格式非法(须为 dict,实为 {type(signature).__name__}) "
            f"→ 改成 {{字段:值}} 8 字段块"
        )]

    # 检查必需字段
    missing = [k for k in SIGNATURE_FIELDS if not str(signature.get(k, "")).strip()]

    if missing:
        return [(
            Severity.FAIL,
            f"视听签名缺字段: {', '.join(missing)} → 补全 8 字段"
        )]
    else:
        return [(Severity.OK, "视听签名 8 字段齐全")]


# 创建规则卡片
rule_signature = RuleCard(
    id="R017",
    name="版权署名",
    category=RuleCategory.TECHNICAL,
    rule=check_signature,
    severity=Severity.FAIL,
    description="检查视听签名块的8字段完整性",
    examples=[
        '✅ signature 包含 8 个必需字段',
        '❌ signature 缺少 author 字段 → FAIL'
    ],
    rationale="合规要求，特别是使用 CC-BY 素材时必须署名",
    references=["AiFilm-pipeline/code/validators.py:_g13_signature"],
    priority=70,
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("版权署名规则测试")
    print("=" * 60)

    # 测试1: 完整签名
    class PassModel:
        signature = {
            "project_name": "AiFilm V2",
            "author": "Team",
            "license": "MIT",
            "genre": "Drama",
            "style": "Cinematic",
            "mood": "Tense",
            "camera_emotion": "Intimate",
            "director_dna": "Visual",
        }

    result = rule_signature.apply(PassModel())
    print(f"\n测试1 - 完整签名:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 缺失字段
    class FailModel:
        signature = {
            "project_name": "AiFilm V2",
            "author": "Team",
        }

    result = rule_signature.apply(FailModel())
    print(f"\n测试2 - 缺失字段:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    print("\n" + "=" * 60)
