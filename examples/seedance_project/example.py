#!/usr/bin/env python3
"""
Seedance 项目示例

展示如何使用 AiFilm V2.0 创建和验证 Seedance 项目。

运行:
    python examples/seedance_project/example.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core import Pipeline, RuleEngine
from core.rule_card import Severity


# ===== 创建示例项目数据 =====

class SeedanceProject:
    """Seedance 项目示例"""

    def __init__(self):
        # 项目类型
        self.is_seedance = True
        self.is_h3 = False

        # 五等式数据
        self.n_sub = 3  # 3个子单元
        self.n_sb = 3   # 3个故事板
        self.n_vid = 3  # 3个视频prompt
        self.n_sty = 3  # 3个Style
        self.n_anc = 3  # 3个锚定

        # Prompt 块（用于八段检查）
        self.prompt_blocks = [
            """
SHOT_META: 镜1 · 城市街道 · 白天
Dynamic: 侦探推开车门，走向公交车站，目光扫过街道
Static: 繁忙的城市街道，人来人往
Camera: 跟镜，从车内跟随侦探
Optics: 35mm镜头，景深适中
Style & Mood: 都市感，略带紧张
Audio: 环境音-街道嘈杂，车门关闭声
SHOT_ASSETS: 侦探-正装，城市街道场景
            """.strip(),
            """
SHOT_META: 镜2 · 公交车站 · 白天
Dynamic: 侦探站在车站，拿出手机查看信息
Static: 公交车站牌，背景是行驶的车辆
Camera: 中景，固定镜头
Optics: 50mm镜头
Style & Mood: 日常感，略显疲惫
Audio: 环境音-车辆行驶，手机提示音
SHOT_ASSETS: 侦探-正装，手机道具
            """.strip(),
            """
SHOT_META: 镜3 · 车站特写 · 白天
Dynamic: 镜头推向侦探的脸部，表情凝重
Static: 侦探面部特写，背景虚化
Camera: 推镜
Optics: 85mm镜头，大光圈
Style & Mood: 紧张感，情绪转折
Audio: 环境音减弱，突出呼吸声
SHOT_ASSETS: 侦探-特写表情
            """.strip(),
        ]

        # 对白块
        self.dialogue_blocks = [
            '侦探:"这里发生了什么？"',
            '路人:"不知道，我只是路过"',
        ]

        # 预算
        self.zh_budget = 1000
        self.zh_used = 856

        # 时长
        self.duration = 15  # 总时长 15s


# ===== 运行示例 =====

def main():
    print("=" * 70)
    print("AiFilm V2.0 - Seedance 项目示例")
    print("=" * 70)

    # 创建项目
    project = SeedanceProject()

    print("\n项目信息:")
    print(f"  项目类型: Seedance")
    print(f"  子单元数: {project.n_sub}")
    print(f"  视频prompt数: {project.n_vid}")
    print(f"  总时长: {project.duration}s")
    print(f"  字数: {project.zh_used}/{project.zh_budget}")

    # 创建管线（auto_load_rules=True 会自动加载规则）
    pipeline = Pipeline()

    # 检查规则加载状态
    stats = pipeline.engine.stats()
    print(f"\n已加载 {stats['total_rules']} 个规则")

    # 验证项目
    print("\n" + "=" * 70)
    print("开始验证...")
    print("=" * 70)

    report = pipeline.validate(project, project_type="seedance")

    # 打印结果
    print(f"\n验证报告:")
    print(f"  总计: {report['total']}")
    print(f"  ✅ 通过: {report['passed']}")
    print(f"  ❌ 失败: {report['failed']}")
    print(f"  ⚠️  警告: {report['warnings']}")
    print(f"  ℹ️  信息: {report['infos']}")

    # 详细结果
    if report['results']:
        print(f"\n详细结果:")
        for result in report['results']:
            severity = result['severity']
            icon = {'FAIL': '❌', 'WARN': '⚠️', 'INFO': 'ℹ️', 'OK': '✅'}.get(severity, '•')
            print(f"  {icon} [{result['rule_name']}] {result['message']}")

    # 总结
    print("\n" + "=" * 70)
    if report['failed'] == 0:
        print("✅ 项目验证通过！可以继续生产。")
    else:
        print(f"❌ 项目存在 {report['failed']} 个错误，需要修复。")
    print("=" * 70)


if __name__ == "__main__":
    main()
