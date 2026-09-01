#!/usr/bin/env python3
"""
RuleCard 单元测试

测试 RuleCard 基类的所有功能。

运行测试:
    python -m pytest tests/unit/test_rule_card.py -v
    或
    python tests/unit/test_rule_card.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.rule_card import (
    RuleCard,
    RuleCategory,
    Severity,
    AppliesTo,
    structure_rule,
    style_rule,
    content_rule,
    technical_rule,
    h3_rule,
)


def test_rule_card_creation():
    """测试创建 RuleCard"""
    rule = RuleCard(
        id="R001",
        name="测试规则",
        category=RuleCategory.STRUCTURE,
        description="这是一个测试规则"
    )

    assert rule.id == "R001"
    assert rule.name == "测试规则"
    assert rule.category == RuleCategory.STRUCTURE
    assert rule.version == "1.0.0"
    assert rule.priority == 50


def test_rule_card_with_logic():
    """测试带逻辑的 RuleCard"""
    def check_logic(context):
        return context.value > 0

    rule = RuleCard(
        id="R002",
        name="正数检查",
        category=RuleCategory.TECHNICAL,
        rule=check_logic,
    )

    class MockContext:
        value = 5

    context = MockContext()
    result = rule.apply(context)
    assert result == True


def test_rule_card_should_apply_all():
    """测试 applies_to=ALL 的规则"""
    rule = RuleCard(
        id="R003",
        name="通用规则",
        category=RuleCategory.STRUCTURE,
        applies_to=AppliesTo.ALL,
    )

    class SeedanceContext:
        is_seedance = True

    class H3Context:
        is_h3 = True

    assert rule.should_apply(SeedanceContext())
    assert rule.should_apply(H3Context())


def test_rule_card_should_apply_seedance():
    """测试 applies_to=SEEDANCE 的规则"""
    rule = RuleCard(
        id="R004",
        name="Seedance 专用规则",
        category=RuleCategory.SEEDANCE,
        applies_to=AppliesTo.SEEDANCE,
    )

    class SeedanceContext:
        is_seedance = True

    class H3Context:
        is_h3 = True

    assert rule.should_apply(SeedanceContext())
    assert not rule.should_apply(H3Context())


def test_rule_card_should_apply_h3():
    """测试 applies_to=H3 的规则"""
    rule = RuleCard(
        id="R005",
        name="H3 专用规则",
        category=RuleCategory.H3,
        applies_to=AppliesTo.H3,
    )

    class SeedanceContext:
        is_seedance = True

    class H3Context:
        is_h3 = True

    assert not rule.should_apply(SeedanceContext())
    assert rule.should_apply(H3Context())


def test_rule_card_with_when_condition():
    """测试自定义 when 条件"""
    rule = RuleCard(
        id="R006",
        name="条件规则",
        category=RuleCategory.CONTENT,
        when=lambda ctx: hasattr(ctx, 'shots') and len(ctx.shots) > 5,
    )

    class SmallContext:
        shots = [1, 2, 3]

    class LargeContext:
        shots = [1, 2, 3, 4, 5, 6]

    assert not rule.should_apply(SmallContext())
    assert rule.should_apply(LargeContext())


def test_rule_card_validation():
    """测试规则验证"""
    def validate_output(output):
        if output < 0:
            return [(Severity.FAIL, "值不能为负")]
        if output > 100:
            return [(Severity.WARN, "值过大")]
        return [(Severity.OK, "通过")]

    rule = RuleCard(
        id="R007",
        name="范围检查",
        category=RuleCategory.TECHNICAL,
        rule=lambda ctx: ctx.value,
        validate=validate_output,
    )

    # 测试负值
    class NegativeContext:
        value = -5

    result = rule.apply(NegativeContext())
    validations = rule.validate_output(result)
    assert len(validations) == 1
    assert validations[0][0] == Severity.FAIL

    # 测试过大值
    class LargeContext:
        value = 150

    result = rule.apply(LargeContext())
    validations = rule.validate_output(result)
    assert len(validations) == 1
    assert validations[0][0] == Severity.WARN

    # 测试正常值
    class NormalContext:
        value = 50

    result = rule.apply(NormalContext())
    validations = rule.validate_output(result)
    assert len(validations) == 1
    assert validations[0][0] == Severity.OK


def test_convenience_functions():
    """测试便捷创建函数"""
    # structure_rule
    r1 = structure_rule("R001", "结构规则", lambda ctx: None)
    assert r1.category == RuleCategory.STRUCTURE
    assert r1.severity == Severity.FAIL

    # style_rule
    r2 = style_rule("R002", "风格规则", lambda ctx: None)
    assert r2.category == RuleCategory.STYLE
    assert r2.severity == Severity.WARN

    # content_rule
    r3 = content_rule("R003", "内容规则", lambda ctx: None)
    assert r3.category == RuleCategory.CONTENT

    # technical_rule
    r4 = technical_rule("R004", "技术规则", lambda ctx: None)
    assert r4.category == RuleCategory.TECHNICAL
    assert r4.severity == Severity.FAIL

    # h3_rule
    r5 = h3_rule("R005", "H3规则", lambda ctx: None)
    assert r5.category == RuleCategory.H3
    assert r5.applies_to == AppliesTo.H3


def test_rule_card_to_dict():
    """测试导出为字典"""
    rule = RuleCard(
        id="R008",
        name="测试规则",
        category=RuleCategory.STRUCTURE,
        description="描述",
        examples=["示例1", "示例2"],
        tags=["tag1", "tag2"],
    )

    d = rule.to_dict()
    assert d['id'] == "R008"
    assert d['name'] == "测试规则"
    assert d['category'] == "structure"
    assert d['description'] == "描述"
    assert len(d['examples']) == 2
    assert len(d['tags']) == 2


def run_all_tests():
    """运行所有测试"""
    tests = [
        ("创建 RuleCard", test_rule_card_creation),
        ("带逻辑的 RuleCard", test_rule_card_with_logic),
        ("applies_to=ALL", test_rule_card_should_apply_all),
        ("applies_to=SEEDANCE", test_rule_card_should_apply_seedance),
        ("applies_to=H3", test_rule_card_should_apply_h3),
        ("自定义 when 条件", test_rule_card_with_when_condition),
        ("规则验证", test_rule_card_validation),
        ("便捷创建函数", test_convenience_functions),
        ("导出为字典", test_rule_card_to_dict),
    ]

    passed = 0
    failed = 0

    print("=" * 60)
    print("RuleCard 单元测试")
    print("=" * 60)

    for name, test_func in tests:
        try:
            test_func()
            print(f"  ✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ {name}: {type(e).__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
