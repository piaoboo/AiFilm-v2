#!/usr/bin/env python3
"""
资产卡 §E 六维完整性规则

检查资产卡 §E 全局视觉指纹段的六维完整性：
1. 构图节奏
2. 色彩调性
3. 镜头质感
4. 光影氛围
5. 方言/题材负向
6. 关键帧锚定

迁移自: AiFilm-pipeline validators.py _g30_assetcard_fingerprint
版本: v1.0.0
日期: 2026-09-01
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory

# §E 六维槽位及其别名
E_SLOTS = [
    ("构图节奏", ["构图", "节奏"]),
    ("色彩调性", ["色彩", "调性", "色调"]),
    ("镜头质感", ["镜头", "质感"]),
    ("光影氛围", ["光影", "氛围", "光线"]),
    ("方言/题材负向", ["方言", "负向", "题材"]),
    ("关键帧锚定", ["关键帧", "锚定", "锚点"]),
]


def check_assetcard_fingerprint(model):
    """
    检查资产卡 §E 六维完整性

    Args:
        model: 包含 assetcard 路径的模型对象

    Returns:
        List[tuple]: 验证结果列表
    """
    assetcard_path = getattr(model, 'assetcard', None)

    if not assetcard_path:
        return [(Severity.OK, "§E 视觉指纹闸跳过:未给 assetcard(**未检查,非合规**)")]

    try:
        with open(assetcard_path, encoding='utf-8') as f:
            ac = f.read()
    except Exception as e:
        return [(Severity.WARN, f"无法读取资产卡: {e}")]

    # 查找 §E 段
    match = re.search(r"^##\s*E\s[^\n]*\n(.*?)(?=^##\s|\Z)", ac, re.S | re.M)
    if not match:
        return [(
            Severity.WARN,
            "资产卡未找到 `## E 全局视觉指纹` 段 → §E 六维无从校验;"
            "母版缺席时每一维都会在每集被临时发明"
        )]

    body = match.group(1)

    # 检查六维是否存在
    missing = []
    for name, aliases in E_SLOTS:
        found = any(alias in body for alias in aliases)
        if not found:
            missing.append(name)

    if missing:
        return [(
            Severity.WARN,
            f"§E 缺失维度: {', '.join(missing)} → 建议补充"
        )]
    else:
        return [(Severity.OK, f"§E 六维完整")]


# 创建规则卡片
rule_assetcard_fingerprint = RuleCard(
    id="R015",
    name="资产卡指纹完整性",
    category=RuleCategory.TECHNICAL,
    severity=Severity.WARN,
    priority=70,
    description="检查资产卡 §E 全局视觉指纹段的六维完整性",
    rule=check_assetcard_fingerprint,
    examples=[
        '✅ §E 包含六维：构图节奏、色彩调性、镜头质感、光影氛围、方言/题材负向、关键帧锚定',
        '⚠️ §E 缺失维度：方言/题材负向 → WARN'
    ],
    rationale="缺维会导致每条 prompt 临时发明风格，跨条不一致",
    references=["AiFilm-pipeline/code/validators.py:_g30_assetcard_fingerprint"],
    version="1.0.0",
)


if __name__ == "__main__":
    print("=" * 60)
    print("资产卡指纹完整性规则测试")
    print("=" * 60)

    # 测试1: 无资产卡
    class NoAssetcardModel:
        pass

    result = rule_assetcard_fingerprint.apply(NoAssetcardModel())
    print(f"\n测试1 - 无资产卡:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 测试2: 创建临时资产卡（完整六维）
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("""
## E 全局视觉指纹

1. 构图节奏：史诗感构图
2. 色彩调性：高对比暗调
3. 镜头质感：电影质感
4. 光影氛围：戏剧性光影
5. 方言/题材负向：避免卡通化
6. 关键帧锚定：关键帧固定
        """)
        temp_path = f.name

    class CompleteModel:
        assetcard = temp_path

    result = rule_assetcard_fingerprint.apply(CompleteModel())
    print(f"\n测试2 - 完整六维:")
    for severity, message in result:
        print(f"  {severity.value}: {message}")

    # 清理临时文件
    import os
    os.unlink(temp_path)

    print("\n" + "=" * 60)
