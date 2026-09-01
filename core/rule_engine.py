#!/usr/bin/env python3
"""
规则引擎

负责加载、管理和执行 RuleCard。

核心功能：
1. 规则注册与发现
2. 规则依赖解析
3. 规则执行调度
4. 结果聚合

版本: v0.1.0
日期: 2026-09-01
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
import importlib
import inspect
from pathlib import Path

from .rule_card import RuleCard, RuleCategory, AppliesTo, Severity


class RuleEngine:
    """
    规则引擎

    管理所有 RuleCard 的生命周期，负责：
    - 注册和发现规则
    - 解析规则依赖
    - 按优先级和依赖顺序执行规则
    - 聚合执行结果

    Example:
        >>> engine = RuleEngine()
        >>> engine.register(my_rule)
        >>> results = engine.execute(model)
    """

    def __init__(self):
        self._rules: Dict[str, RuleCard] = {}  # id -> RuleCard
        self._by_category: Dict[RuleCategory, List[str]] = defaultdict(list)
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)

    def register(self, rule: RuleCard) -> None:
        """
        注册一个规则

        Args:
            rule: 要注册的 RuleCard

        Raises:
            ValueError: 如果规则 ID 已存在
        """
        if rule.id in self._rules:
            raise ValueError(f"Rule ID {rule.id} already registered")

        self._rules[rule.id] = rule
        self._by_category[rule.category].append(rule.id)

        # 构建依赖图
        for dep_id in rule.depends_on:
            self._dependency_graph[rule.id].add(dep_id)

    def register_module(self, module_path: str) -> int:
        """
        从 Python 模块注册所有规则

        Args:
            module_path: 模块路径（如 "rules.structure.five_equations"）

        Returns:
            int: 注册的规则数量
        """
        module = importlib.import_module(module_path)
        count = 0

        for name, obj in inspect.getmembers(module):
            if isinstance(obj, RuleCard):
                self.register(obj)
                count += 1

        return count

    def register_directory(self, directory: Path) -> int:
        """
        从目录注册所有规则模块

        Args:
            directory: 规则目录路径

        Returns:
            int: 注册的规则数量
        """
        count = 0
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            # 构建模块路径
            relative = py_file.relative_to(directory.parent)
            module_path = str(relative.with_suffix("")).replace("/", ".")

            try:
                count += self.register_module(module_path)
            except Exception as e:
                print(f"Warning: Failed to load {module_path}: {e}")

        return count

    def get_rule(self, rule_id: str) -> Optional[RuleCard]:
        """获取指定 ID 的规则"""
        return self._rules.get(rule_id)

    def get_rules_by_category(self, category: RuleCategory) -> List[RuleCard]:
        """获取指定类别的所有规则"""
        rule_ids = self._by_category.get(category, [])
        return [self._rules[rid] for rid in rule_ids]

    def get_applicable_rules(
        self,
        context: Any,
        category: Optional[RuleCategory] = None,
        tags: Optional[List[str]] = None
    ) -> List[RuleCard]:
        """
        获取适用于给定上下文的所有规则

        Args:
            context: 上下文对象
            category: 可选的类别过滤
            tags: 可选的标签过滤

        Returns:
            适用的规则列表（按优先级排序）
        """
        rules = []

        for rule in self._rules.values():
            # 类别过滤
            if category and rule.category != category:
                continue

            # 标签过滤
            if tags and not any(tag in rule.tags for tag in tags):
                continue

            # 检查是否适用
            if rule.should_apply(context):
                rules.append(rule)

        # 按优先级排序（高优先级先执行）
        rules.sort(key=lambda r: r.priority, reverse=True)

        return rules

    def _resolve_execution_order(self, rule_ids: List[str]) -> List[str]:
        """
        根据依赖关系解析执行顺序（拓扑排序）

        Args:
            rule_ids: 要执行的规则 ID 列表

        Returns:
            排序后的规则 ID 列表

        Raises:
            ValueError: 如果存在循环依赖
        """
        # 构建子图
        in_degree = {rid: 0 for rid in rule_ids}
        subgraph = {rid: set() for rid in rule_ids}

        for rid in rule_ids:
            deps = self._dependency_graph.get(rid, set())
            # 只考虑在执行列表中的依赖
            deps = deps & set(rule_ids)
            for dep in deps:
                subgraph[dep].add(rid)
                in_degree[rid] += 1

        # 拓扑排序（Kahn 算法）
        queue = [rid for rid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # 按优先级排序队列
            queue.sort(key=lambda r: self._rules[r].priority, reverse=True)
            current = queue.pop(0)
            result.append(current)

            for neighbor in subgraph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(rule_ids):
            raise ValueError("Circular dependency detected in rules")

        return result

    def execute(
        self,
        context: Any,
        category: Optional[RuleCategory] = None,
        rule_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行规则

        Args:
            context: 上下文对象
            category: 可选的类别过滤
            rule_ids: 可选的规则 ID 列表（如果指定，只执行这些规则）

        Returns:
            执行结果列表，每个元素包含：
            {
                'rule_id': str,
                'rule_name': str,
                'status': 'success' | 'skipped' | 'error',
                'result': Any,
                'validations': List[tuple],
                'error': Optional[str]
            }
        """
        # 确定要执行的规则
        if rule_ids:
            rules = [self._rules[rid] for rid in rule_ids if rid in self._rules]
        else:
            rules = self.get_applicable_rules(context, category=category)

        if not rules:
            return []

        # 解析执行顺序
        ordered_ids = self._resolve_execution_order([r.id for r in rules])

        # 执行规则
        results = []
        for rule_id in ordered_ids:
            rule = self._rules[rule_id]
            result_entry = {
                'rule_id': rule.id,
                'rule_name': rule.name,
                'status': 'success',
                'result': None,
                'validations': [],
                'error': None
            }

            try:
                # 检查是否应该应用
                if not rule.should_apply(context):
                    result_entry['status'] = 'skipped'
                    results.append(result_entry)
                    continue

                # 执行规则
                output = rule.apply(context)
                result_entry['result'] = output

                # 验证输出
                if rule.validate:
                    validations = rule.validate_output(output)
                    result_entry['validations'] = validations

            except Exception as e:
                result_entry['status'] = 'error'
                result_entry['error'] = str(e)

            results.append(result_entry)

        return results

    def validate(
        self,
        context: Any,
        category: Optional[RuleCategory] = None
    ) -> Dict[str, Any]:
        """
        验证上下文（只执行验证规则）

        Args:
            context: 上下文对象
            category: 可选的类别过滤

        Returns:
            验证报告：
            {
                'total': int,
                'passed': int,
                'failed': int,
                'warnings': int,
                'results': List[Dict]
            }
        """
        results = self.execute(context, category=category)

        report = {
            'total': len(results),
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'infos': 0,
            'errors': 0,
            'results': []
        }

        for result in results:
            if result['status'] == 'error':
                report['errors'] += 1
                report['results'].append(result)
                continue

            if result['status'] == 'skipped':
                continue

            # 统计验证结果
            for severity, message in result.get('validations', []):
                entry = {
                    'rule_id': result['rule_id'],
                    'rule_name': result['rule_name'],
                    'severity': severity.value if hasattr(severity, 'value') else str(severity),
                    'message': message
                }

                if severity == Severity.FAIL or str(severity) == 'FAIL':
                    report['failed'] += 1
                elif severity == Severity.WARN or str(severity) == 'WARN':
                    report['warnings'] += 1
                elif severity == Severity.INFO or str(severity) == 'INFO':
                    report['infos'] += 1
                elif severity == Severity.OK or str(severity) == 'OK':
                    report['passed'] += 1

                report['results'].append(entry)

        return report

    def stats(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        by_category = {}
        for cat, rule_ids in self._by_category.items():
            by_category[cat.value] = len(rule_ids)

        by_applies_to = defaultdict(int)
        for rule in self._rules.values():
            by_applies_to[rule.applies_to.value] += 1

        return {
            'total_rules': len(self._rules),
            'by_category': by_category,
            'by_applies_to': dict(by_applies_to),
            'has_dependencies': sum(1 for r in self._rules.values() if r.depends_on),
        }

    def __repr__(self) -> str:
        return f"RuleEngine(rules={len(self._rules)})"


if __name__ == "__main__":
    # 示例：使用规则引擎
    from rule_card import technical_rule, Severity

    # 创建规则引擎
    engine = RuleEngine()

    # 创建示例规则
    def check_duration(model):
        duration = getattr(model, 'duration', 0)
        if duration <= 0:
            return [(Severity.FAIL, "时长必须大于0")]
        if duration > 30:
            return [(Severity.WARN, f"时长{duration}s超过推荐的30s")]
        return [(Severity.OK, f"时长{duration}s合理")]

    rule = technical_rule(
        id="R011",
        name="时长验证",
        rule=check_duration,
        validate=lambda output: output,
        description="验证单个镜头的时长"
    )

    # 注册规则
    engine.register(rule)

    # 打印统计
    print("规则引擎统计:")
    print(engine.stats())

    # 创建测试上下文
    class MockModel:
        duration = 25

    context = MockModel()

    # 执行验证
    report = engine.validate(context)
    print(f"\n验证报告:")
    print(f"  总计: {report['total']}")
    print(f"  通过: {report['passed']}")
    print(f"  失败: {report['failed']}")
    print(f"  警告: {report['warnings']}")
