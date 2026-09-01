#!/usr/bin/env python3
"""
RuleEngine 单元测试

测试规则引擎的所有功能。

运行测试:
    python tests/unit/test_rule_engine.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.rule_card import RuleCard, RuleCategory, Severity, structure_rule, style_rule
from core.rule_engine import RuleEngine


def test_engine_creation():
    """测试创建引擎"""
    engine = RuleEngine()
    assert len(engine._rules) == 0


def test_register_rule():
    """测试注册规则"""
    engine = RuleEngine()
    rule = structure_rule("R001", "测试规则", lambda ctx: None)

    engine.register(rule)
    assert len(engine._rules) == 1
    assert engine.get_rule("R001") == rule


def test_register_duplicate_raises():
    """测试注册重复 ID 抛出异常"""
    engine = RuleEngine()
    rule1 = structure_rule("R001", "规则1", lambda ctx: None)
    rule2 = structure_rule("R001", "规则2", lambda ctx: None)

    engine.register(rule1)

    try:
        engine.register(rule2)
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "already registered" in str(e)


def test_get_rules_by_category():
    """测试按类别获取规则"""
    engine = RuleEngine()

    r1 = structure_rule("R001", "结构1", lambda ctx: None)
    r2 = structure_rule("R002", "结构2", lambda ctx: None)
    r3 = style_rule("R003", "风格1", lambda ctx: None)

    engine.register(r1)
    engine.register(r2)
    engine.register(r3)

    structure_rules = engine.get_rules_by_category(RuleCategory.STRUCTURE)
    assert len(structure_rules) == 2

    style_rules = engine.get_rules_by_category(RuleCategory.STYLE)
    assert len(style_rules) == 1


def test_get_applicable_rules():
    """测试获取适用规则"""
    engine = RuleEngine()

    r1 = structure_rule("R001", "高优先级", lambda ctx: None, priority=100)
    r2 = structure_rule("R002", "低优先级", lambda ctx: None, priority=10)

    engine.register(r1)
    engine.register(r2)

    class MockContext:
        pass

    rules = engine.get_applicable_rules(MockContext())
    assert len(rules) == 2
    # 验证按优先级排序
    assert rules[0].id == "R001"
    assert rules[1].id == "R002"


def test_execute_rules():
    """测试执行规则"""
    engine = RuleEngine()

    def add_one(ctx):
        return ctx.value + 1

    rule = structure_rule("R001", "加一", add_one)
    engine.register(rule)

    class MockContext:
        value = 5

    results = engine.execute(MockContext())
    assert len(results) == 1
    assert results[0]['rule_id'] == "R001"
    assert results[0]['status'] == 'success'
    assert results[0]['result'] == 6


def test_execute_with_validation():
    """测试执行带验证的规则"""
    engine = RuleEngine()

    def check_positive(ctx):
        return ctx.value

    def validate(output):
        if output < 0:
            return [(Severity.FAIL, "值为负")]
        return [(Severity.OK, "通过")]

    rule = structure_rule("R001", "正数检查", check_positive, validate=validate)
    engine.register(rule)

    class PositiveContext:
        value = 10

    results = engine.execute(PositiveContext())
    assert len(results[0]['validations']) == 1
    assert results[0]['validations'][0][0] == Severity.OK


def test_resolve_dependencies():
    """测试依赖解析"""
    engine = RuleEngine()

    # R002 依赖 R001
    r1 = structure_rule("R001", "基础规则", lambda ctx: None)
    r2 = structure_rule("R002", "依赖规则", lambda ctx: None, depends_on=["R001"])

    engine.register(r1)
    engine.register(r2)

    # 执行顺序应该是 R001 -> R002
    order = engine._resolve_execution_order(["R001", "R002"])
    assert order == ["R001", "R002"]

    # 反向注册顺序也应该正确
    order = engine._resolve_execution_order(["R002", "R001"])
    assert order == ["R001", "R002"]


def test_validate_report():
    """测试验证报告"""
    engine = RuleEngine()

    def check_range(ctx):
        return ctx.value

    def validate(output):
        if output < 0:
            return [(Severity.FAIL, "负数")]
        if output > 100:
            return [(Severity.WARN, "过大")]
        return [(Severity.OK, "正常")]

    rule = structure_rule("R001", "范围检查", check_range, validate=validate)
    engine.register(rule)

    class MockContext:
        value = 50

    report = engine.validate(MockContext())
    assert report['total'] == 1
    assert report['passed'] == 1
    assert report['failed'] == 0


def test_engine_stats():
    """测试引擎统计"""
    engine = RuleEngine()

    r1 = structure_rule("R001", "结构1", lambda ctx: None)
    r2 = style_rule("R002", "风格1", lambda ctx: None)

    engine.register(r1)
    engine.register(r2)

    stats = engine.stats()
    assert stats['total_rules'] == 2
    assert stats['by_category']['structure'] == 1
    assert stats['by_category']['style'] == 1


def run_all_tests():
    """运行所有测试"""
    tests = [
        ("创建引擎", test_engine_creation),
        ("注册规则", test_register_rule),
        ("注册重复ID", test_register_duplicate_raises),
        ("按类别获取规则", test_get_rules_by_category),
        ("获取适用规则", test_get_applicable_rules),
        ("执行规则", test_execute_rules),
        ("执行带验证的规则", test_execute_with_validation),
        ("依赖解析", test_resolve_dependencies),
        ("验证报告", test_validate_report),
        ("引擎统计", test_engine_stats),
    ]

    passed = 0
    failed = 0

    print("=" * 60)
    print("RuleEngine 单元测试")
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
