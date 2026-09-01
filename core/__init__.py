"""
AiFilm V2.0 Core Module

核心模块包含：
- RuleCard: 规则卡片基类
- RuleEngine: 规则引擎
- ContextManager: Context 管理器

版本: v0.1.0
日期: 2026-09-01
"""

from .rule_card import (
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

from .rule_engine import RuleEngine

from .context_manager import (
    ContextManager,
    ContextBudget,
    LoadingStrategy,
)

__version__ = "0.1.0"

__all__ = [
    # RuleCard
    "RuleCard",
    "RuleCategory",
    "Severity",
    "AppliesTo",
    "structure_rule",
    "style_rule",
    "content_rule",
    "technical_rule",
    "h3_rule",
    # RuleEngine
    "RuleEngine",
    # ContextManager
    "ContextManager",
    "ContextBudget",
    "LoadingStrategy",
]
