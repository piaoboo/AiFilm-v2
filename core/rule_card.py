#!/usr/bin/env python3
"""
RuleCard 基类

规则卡片是 AiFilm V2 的核心抽象，统一表示所有生成和验证规则。

设计原则：
1. 声明式 - 规则定义与执行分离
2. 组合式 - 规则可以组合和继承
3. 可测试 - 每个规则都可以独立测试
4. 自文档 - 规则包含完整的元数据和示例

版本: v0.1.0
日期: 2026-09-01
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any, Dict
from enum import Enum


class RuleCategory(Enum):
    """规则类别"""
    STRUCTURE = "structure"    # 结构规则（五等式、八段等）
    STYLE = "style"            # 风格规则（风格标签、署名等）
    CONTENT = "content"        # 内容规则（对白、动作、VFX等）
    TECHNICAL = "technical"    # 技术规则（时长、预算、分辨率等）
    H3 = "h3"                  # H3 专用规则
    SEEDANCE = "seedance"      # Seedance 专用规则


class Severity(Enum):
    """验证严重程度"""
    FAIL = "FAIL"      # 硬闸，必须修复
    WARN = "WARN"      # 警告，建议修复
    INFO = "INFO"      # 信息，仅提示
    OK = "OK"          # 通过


class AppliesTo(Enum):
    """适用范围"""
    ALL = "all"            # 所有项目
    SEEDANCE = "seedance"  # Seedance 项目
    H3 = "h3"              # H3 项目
    CUSTOM = "custom"      # 自定义条件


@dataclass
class RuleCard:
    """
    规则卡片基类

    每个 RuleCard 代表一个独立的规则，包含：
    - 元数据：ID、名称、类别、优先级
    - 触发条件：何时应用此规则
    - 规则逻辑：生成或验证逻辑
    - 验证：如何验证输出
    - 文档：描述、示例、理由

    Example:
        >>> card = RuleCard(
        ...     id="R001",
        ...     name="五等式结构",
        ...     category=RuleCategory.STRUCTURE,
        ...     rule=lambda m: check_five_equations(m),
        ...     description="检查五个计数是否严格相等"
        ... )
    """

    # ===== 元数据 =====
    id: str                              # 规则唯一标识（如 R001, G046）
    name: str                            # 规则名称
    category: RuleCategory               # 规则类别
    version: str = "1.0.0"               # 版本号
    priority: int = 50                   # 优先级（1-100，越高越优先）

    # ===== 触发条件 =====
    when: Optional[Callable[[Any], bool]] = None     # 触发条件函数
    applies_to: AppliesTo = AppliesTo.ALL            # 适用范围

    # ===== 规则内容 =====
    rule: Optional[Callable[[Any], Any]] = None      # 规则逻辑（生成或验证）
    template: Optional[str] = None                   # 模板字符串（用于生成）

    # ===== 验证 =====
    validate: Optional[Callable[[Any], List[tuple]]] = None  # 验证函数
    severity: Severity = Severity.WARN                        # 默认严重程度

    # ===== 文档 =====
    description: str = ""                # 规则描述
    examples: List[str] = field(default_factory=list)  # 使用示例
    rationale: str = ""                  # 设计理由
    references: List[str] = field(default_factory=list)  # 参考文档

    # ===== 依赖 =====
    depends_on: List[str] = field(default_factory=list)  # 依赖的其他规则ID
    conflicts_with: List[str] = field(default_factory=list)  # 冲突的规则ID

    # ===== 元信息 =====
    tags: List[str] = field(default_factory=list)  # 标签
    author: str = ""                     # 作者
    created_at: str = ""                 # 创建时间
    updated_at: str = ""                 # 更新时间

    def should_apply(self, context: Any) -> bool:
        """
        判断规则是否应该应用到给定上下文

        Args:
            context: 上下文对象（通常是 Model 或 Shot）

        Returns:
            bool: 是否应该应用此规则
        """
        # 检查适用范围
        if self.applies_to == AppliesTo.SEEDANCE:
            if not getattr(context, 'is_seedance', False):
                return False
        elif self.applies_to == AppliesTo.H3:
            if not getattr(context, 'is_h3', False):
                return False

        # 检查自定义条件
        if self.when is not None:
            return self.when(context)

        return True

    def apply(self, context: Any) -> Any:
        """
        应用规则到给定上下文

        Args:
            context: 上下文对象

        Returns:
            规则执行结果（生成的内容或验证结果）
        """
        if not self.should_apply(context):
            return None

        if self.rule is None:
            raise ValueError(f"Rule {self.id} has no rule function defined")

        return self.rule(context)

    def validate_output(self, output: Any) -> List[tuple]:
        """
        验证规则输出

        Args:
            output: 规则的输出结果

        Returns:
            List[tuple]: 验证结果列表，每个元素为 (severity, message)
        """
        if self.validate is None:
            return [(Severity.OK, f"Rule {self.id} validation passed (no validator)")]

        return self.validate(output)

    def __repr__(self) -> str:
        return f"RuleCard(id={self.id}, name={self.name}, category={self.category.value})"

    def to_dict(self) -> Dict:
        """导出为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'version': self.version,
            'priority': self.priority,
            'applies_to': self.applies_to.value,
            'severity': self.severity.value,
            'description': self.description,
            'examples': self.examples,
            'rationale': self.rationale,
            'references': self.references,
            'depends_on': self.depends_on,
            'conflicts_with': self.conflicts_with,
            'tags': self.tags,
        }


# ===== 便捷函数 =====

def structure_rule(id: str, name: str, rule: Callable, **kwargs) -> RuleCard:
    """创建结构规则的便捷函数"""
    return RuleCard(
        id=id,
        name=name,
        category=RuleCategory.STRUCTURE,
        rule=rule,
        severity=Severity.FAIL,  # 结构规则通常是硬闸
        **kwargs
    )


def style_rule(id: str, name: str, rule: Callable, **kwargs) -> RuleCard:
    """创建风格规则的便捷函数"""
    return RuleCard(
        id=id,
        name=name,
        category=RuleCategory.STYLE,
        rule=rule,
        severity=Severity.WARN,  # 风格规则通常是软闸
        **kwargs
    )


def content_rule(id: str, name: str, rule: Callable, **kwargs) -> RuleCard:
    """创建内容规则的便捷函数"""
    return RuleCard(
        id=id,
        name=name,
        category=RuleCategory.CONTENT,
        rule=rule,
        **kwargs
    )


def technical_rule(id: str, name: str, rule: Callable, **kwargs) -> RuleCard:
    """创建技术规则的便捷函数"""
    return RuleCard(
        id=id,
        name=name,
        category=RuleCategory.TECHNICAL,
        rule=rule,
        severity=Severity.FAIL,  # 技术规则通常是硬闸
        **kwargs
    )


def h3_rule(id: str, name: str, rule: Callable, **kwargs) -> RuleCard:
    """创建 H3 专用规则的便捷函数"""
    return RuleCard(
        id=id,
        name=name,
        category=RuleCategory.H3,
        rule=rule,
        applies_to=AppliesTo.H3,
        **kwargs
    )


if __name__ == "__main__":
    # 示例：创建一个简单的规则
    def check_duration(model):
        """检查时长是否在合理范围"""
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
        description="验证单个镜头的时长在合理范围内",
        examples=["✅ 29s", "❌ 0s", "⚠️ 35s"],
        rationale="Seedance 2.5 API 限制单镜最长30s"
    )

    print(rule)
    print(f"\n规则详情:")
    print(f"  ID: {rule.id}")
    print(f"  名称: {rule.name}")
    print(f"  类别: {rule.category.value}")
    print(f"  描述: {rule.description}")
