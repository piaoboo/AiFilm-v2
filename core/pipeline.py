#!/usr/bin/env python3
"""
生成管线

自动化提示词生成管线：
1. 加载适用的规则
2. 组装规则生成提示词
3. 自动验证
4. 生成报告

版本: v0.1.0
日期: 2026-09-01
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .rule_engine import RuleEngine
from .context_manager import ContextManager, ContextBudget
from .rule_card import RuleCategory, Severity


class Pipeline:
    """
    生成管线

    端到端自动化流程：
    1. 读取项目数据
    2. 选择适用规则
    3. 生成提示词
    4. 验证输出
    5. 生成报告

    Example:
        >>> pipeline = Pipeline()
        >>> pipeline.load_rules_from_directory(Path("rules"))
        >>> result = pipeline.generate(project_data)
    """

    def __init__(
        self,
        budget: Optional[ContextBudget] = None,
        auto_load_rules: bool = True
    ):
        self.engine = RuleEngine()
        self.context_manager = ContextManager(budget)
        self.rules_loaded = False

        if auto_load_rules:
            # 尝试从默认位置加载规则
            rules_dir = Path(__file__).parent.parent / "rules"
            if rules_dir.exists():
                self.load_rules_from_directory(rules_dir)

    def load_rules_from_directory(self, directory: Path) -> int:
        """
        从目录加载所有规则

        Args:
            directory: 规则目录路径

        Returns:
            加载的规则数量
        """
        count = self.engine.register_directory(directory)
        self.rules_loaded = count > 0
        return count

    def generate(
        self,
        model: Any,
        project_type: str = "seedance",
        categories: Optional[List[RuleCategory]] = None
    ) -> Dict[str, Any]:
        """
        生成提示词

        Args:
            model: 项目数据模型
            project_type: 项目类型（seedance/h3）
            categories: 要应用的规则类别列表

        Returns:
            生成结果字典
        """
        # 标记项目类型
        if project_type == "seedance":
            model.is_seedance = True
        elif project_type == "h3":
            model.is_h3 = True

        # 获取所有规则
        all_rules = list(self.engine._rules.values())

        # 按 Context 预算选择规则
        selected_rules = self.context_manager.select_rules(
            all_rules,
            model
        )

        # 如果指定了类别，进一步过滤
        if categories:
            selected_rules = [
                r for r in selected_rules
                if r.category in categories
            ]

        # 执行规则
        results = self.engine.execute(
            model,
            rule_ids=[r.id for r in selected_rules]
        )

        # 收集生成的内容
        generated_content = []
        for result in results:
            if result['status'] == 'success' and result['result']:
                generated_content.append({
                    'rule_id': result['rule_id'],
                    'rule_name': result['rule_name'],
                    'content': result['result']
                })

        return {
            'project_type': project_type,
            'rules_applied': len(selected_rules),
            'rules_total': len(all_rules),
            'generated_content': generated_content,
            'execution_results': results
        }

    def validate(
        self,
        model: Any,
        project_type: str = "seedance"
    ) -> Dict[str, Any]:
        """
        验证项目数据

        Args:
            model: 项目数据模型
            project_type: 项目类型

        Returns:
            验证报告
        """
        # 标记项目类型
        if project_type == "seedance":
            model.is_seedance = True
        elif project_type == "h3":
            model.is_h3 = True

        # 执行验证
        report = self.engine.validate(model)

        # 添加项目信息
        report['project_type'] = project_type
        report['rules_total'] = len(self.engine._rules)

        return report

    def generate_and_validate(
        self,
        model: Any,
        project_type: str = "seedance"
    ) -> Dict[str, Any]:
        """
        生成并验证（一体化流程）

        Args:
            model: 项目数据模型
            project_type: 项目类型

        Returns:
            完整结果（生成 + 验证）
        """
        # 生成
        gen_result = self.generate(model, project_type)

        # 验证
        val_result = self.validate(model, project_type)

        return {
            'generation': gen_result,
            'validation': val_result,
            'success': val_result['failed'] == 0
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取管线统计信息"""
        return {
            'engine': self.engine.stats(),
            'context_manager': self.context_manager.get_budget_info(),
            'rules_loaded': self.rules_loaded
        }


if __name__ == "__main__":
    # 测试管线
    print("=" * 60)
    print("生成管线测试")
    print("=" * 60)

    # 创建管线
    pipeline = Pipeline(auto_load_rules=False)

    # 创建测试规则
    from rule_card import structure_rule, Severity

    def test_rule(model):
        return [(Severity.OK, "测试通过")]

    rule = structure_rule(
        id="TEST001",
        name="测试规则",
        rule=test_rule,
        validate=lambda output: output
    )

    pipeline.engine.register(rule)

    # 创建测试模型
    class TestModel:
        n_sub = 5
        n_sb = 5
        n_vid = 5
        n_sty = 5
        n_anc = 5

    # 测试生成
    print("\n生成测试:")
    result = pipeline.generate(TestModel(), project_type="seedance")
    print(f"  应用规则数: {result['rules_applied']}")
    print(f"  总规则数: {result['rules_total']}")

    # 测试验证
    print("\n验证测试:")
    report = pipeline.validate(TestModel(), project_type="seedance")
    print(f"  总计: {report['total']}")
    print(f"  通过: {report['passed']}")
    print(f"  失败: {report['failed']}")

    # 统计信息
    print("\n管线统计:")
    stats = pipeline.get_stats()
    print(f"  规则加载: {stats['rules_loaded']}")
    print(f"  总规则数: {stats['engine']['total_rules']}")

    print("\n" + "=" * 60)
