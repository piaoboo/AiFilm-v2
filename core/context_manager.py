#!/usr/bin/env python3
"""
Context 管理器

负责按需加载和管理规则上下文，优化 token 使用。

核心功能：
1. 按需加载规则（避免 Context 溢出）
2. 规则缓存管理
3. Context 预算控制
4. 规则优先级排序

版本: v0.1.0
日期: 2026-09-01
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

from .rule_card import RuleCard, RuleCategory, AppliesTo


@dataclass
class ContextBudget:
    """Context 预算配置"""
    max_tokens: int = 200000          # 最大 token 数
    reserved_tokens: int = 50000      # 保留 token（用于输出）
    rule_token_estimate: int = 500    # 每个规则平均 token 估算

    @property
    def available_tokens(self) -> int:
        """可用于规则的 token 数"""
        return self.max_tokens - self.reserved_tokens


class ContextManager:
    """
    Context 管理器

    智能管理规则加载，避免 Context 溢出：
    1. 按优先级加载规则
    2. 预估 token 使用
    3. 动态调整加载策略
    4. 缓存常用规则

    Example:
        >>> manager = ContextManager()
        >>> rules = manager.select_rules(context, budget)
    """

    def __init__(self, budget: Optional[ContextBudget] = None):
        self.budget = budget or ContextBudget()
        self._rule_cache: Dict[str, RuleCard] = {}
        self._usage_stats: Dict[str, int] = defaultdict(int)  # rule_id -> usage_count

    def estimate_rule_tokens(self, rule: RuleCard) -> int:
        """
        估算规则占用的 token 数

        Args:
            rule: 规则卡片

        Returns:
            估算的 token 数
        """
        # 简单估算：基于规则的描述、示例等文本长度
        text_length = (
            len(rule.description) +
            sum(len(ex) for ex in rule.examples) +
            len(rule.rationale)
        )

        # 每 4 个字符约等于 1 个 token（粗略估算）
        token_estimate = text_length // 4

        # 加上规则逻辑的基础开销
        token_estimate += self.budget.rule_token_estimate

        return token_estimate

    def select_rules(
        self,
        all_rules: List[RuleCard],
        context: Any,
        max_tokens: Optional[int] = None
    ) -> List[RuleCard]:
        """
        根据 Context 预算智能选择规则

        策略：
        1. 过滤掉不适用的规则
        2. 按优先级排序
        3. 按 token 预算选择
        4. 优先选择常用规则

        Args:
            all_rules: 所有可用规则
            context: 上下文对象
            max_tokens: 可选的 token 上限（覆盖默认预算）

        Returns:
            选中的规则列表
        """
        available = max_tokens or self.budget.available_tokens

        # Step 1: 过滤适用的规则
        applicable = [r for r in all_rules if r.should_apply(context)]

        # Step 2: 按优先级排序（考虑使用频率）
        def priority_score(rule: RuleCard) -> tuple:
            # 第一排序：优先级
            # 第二排序：使用频率
            # 第三排序：是否必须（FAIL 级别）
            is_critical = rule.severity.value == "FAIL"
            usage = self._usage_stats.get(rule.id, 0)
            return (rule.priority, usage, is_critical)

        applicable.sort(key=priority_score, reverse=True)

        # Step 3: 按 token 预算选择
        selected = []
        used_tokens = 0

        for rule in applicable:
            estimated = self.estimate_rule_tokens(rule)

            if used_tokens + estimated <= available:
                selected.append(rule)
                used_tokens += estimated
                self._usage_stats[rule.id] += 1
            else:
                # 预算不足，记录被跳过的规则
                pass

        return selected

    def select_by_category(
        self,
        all_rules: List[RuleCard],
        context: Any,
        categories: List[RuleCategory],
        max_tokens: Optional[int] = None
    ) -> List[RuleCard]:
        """
        按类别选择规则

        Args:
            all_rules: 所有可用规则
            context: 上下文对象
            categories: 要包含的类别列表
            max_tokens: 可选的 token 上限

        Returns:
            选中的规则列表
        """
        # 过滤类别
        filtered = [r for r in all_rules if r.category in categories]

        # 使用通用选择逻辑
        return self.select_rules(filtered, context, max_tokens)

    def select_critical_only(
        self,
        all_rules: List[RuleCard],
        context: Any
    ) -> List[RuleCard]:
        """
        只选择关键规则（FAIL 级别）

        Args:
            all_rules: 所有可用规则
            context: 上下文对象

        Returns:
            选中的规则列表
        """
        critical = [
            r for r in all_rules
            if r.should_apply(context) and r.severity.value == "FAIL"
        ]

        # 关键规则无 token 限制，全部加载
        for rule in critical:
            self._usage_stats[rule.id] += 1

        return critical

    def get_load_strategy(
        self,
        total_rules: int,
        context: Any
    ) -> Dict[str, Any]:
        """
        根据规则数量推荐加载策略

        Args:
            total_rules: 总规则数
            context: 上下文对象

        Returns:
            推荐的加载策略
        """
        max_loadable = self.budget.available_tokens // self.budget.rule_token_estimate

        if total_rules <= max_loadable:
            return {
                'strategy': 'load_all',
                'description': '规则数量少，全部加载',
                'estimated_rules': total_rules
            }
        elif total_rules <= max_loadable * 1.5:
            return {
                'strategy': 'load_by_priority',
                'description': '按优先级加载',
                'estimated_rules': max_loadable
            }
        else:
            return {
                'strategy': 'load_critical_only',
                'description': '只加载关键规则（FAIL 级别）',
                'estimated_rules': max_loadable // 2
            }

    def get_usage_stats(self) -> Dict[str, int]:
        """获取规则使用统计"""
        return dict(self._usage_stats)

    def get_budget_info(self) -> Dict[str, Any]:
        """获取预算信息"""
        return {
            'max_tokens': self.budget.max_tokens,
            'reserved_tokens': self.budget.reserved_tokens,
            'available_tokens': self.budget.available_tokens,
            'rule_token_estimate': self.budget.rule_token_estimate,
            'max_loadable_rules': self.budget.available_tokens // self.budget.rule_token_estimate
        }

    def reset_stats(self) -> None:
        """重置使用统计"""
        self._usage_stats.clear()

    def __repr__(self) -> str:
        return f"ContextManager(budget={self.budget.available_tokens} tokens, tracked={len(self._usage_stats)} rules)"


class LoadingStrategy:
    """规则加载策略枚举"""
    LOAD_ALL = "load_all"                      # 全部加载
    LOAD_BY_PRIORITY = "load_by_priority"      # 按优先级加载
    LOAD_BY_CATEGORY = "load_by_category"      # 按类别加载
    LOAD_CRITICAL_ONLY = "load_critical_only"  # 只加载关键规则


if __name__ == "__main__":
    # 示例：使用 Context 管理器
    from rule_card import structure_rule, style_rule, Severity

    # 创建 Context 管理器
    manager = ContextManager()

    print("Context 预算信息:")
    budget_info = manager.get_budget_info()
    for key, value in budget_info.items():
        print(f"  {key}: {value}")

    # 创建示例规则
    rules = [
        structure_rule(
            id="R001",
            name="五等式结构",
            rule=lambda m: None,
            description="检查五个计数是否严格相等",
            priority=100
        ),
        style_rule(
            id="R005",
            name="风格标签",
            rule=lambda m: None,
            description="验证风格标签的完整性",
            priority=50
        ),
    ]

    # 估算 token 使用
    print(f"\n规则 token 估算:")
    for rule in rules:
        tokens = manager.estimate_rule_tokens(rule)
        print(f"  {rule.id} ({rule.name}): ~{tokens} tokens")

    # 模拟选择规则
    class MockContext:
        pass

    context = MockContext()
    selected = manager.select_rules(rules, context, max_tokens=10000)

    print(f"\n选中规则: {len(selected)}/{len(rules)}")
    for rule in selected:
        print(f"  - {rule.id}: {rule.name} (优先级: {rule.priority})")

    # 推荐加载策略
    strategy = manager.get_load_strategy(50, context)
    print(f"\n推荐加载策略: {strategy['strategy']}")
    print(f"  {strategy['description']}")
    print(f"  预计加载规则数: {strategy['estimated_rules']}")
