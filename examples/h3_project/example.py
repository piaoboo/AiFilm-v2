#!/usr/bin/env python3
"""
H3 项目示例

展示如何使用 AiFilm V2.0 创建和验证 H3 项目。

H3 特性：
- 时长限制：4-15s
- 模式选择：t2va/i2va/ref2va
- 站位承重计算

运行:
    python examples/h3_project/example.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core import Pipeline


# ===== 创建 H3 项目数据 =====

class H3Project:
    """H3 项目示例"""

    def __init__(self):
        # 项目类型
        self.is_seedance = False
        self.is_h3 = True

        # 五等式数据
        self.n_sub = 2
        self.n_sb = 2
        self.n_vid = 2
        self.n_sty = 2
        self.n_anc = 2

        # Prompt 块
        self.prompt_blocks = [
            """
SHOT_META: 镜1 · 室内客厅 · 白天
Dynamic: 两人对坐，A正在说话，B认真倾听
Static: 温馨的客厅，沙发，茶几
Camera: 双人中景
Optics: 35mm
Style & Mood: 温馨，对话感
Audio: 对话，轻音乐
SHOT_ASSETS: 人物A，人物B，客厅场景
            """.strip(),
            """
SHOT_META: 镜2 · 室内客厅 · 白天
Dynamic: B起身倒水，A目送
Static: 同上客厅
Camera: 跟镜
Optics: 50mm
Style & Mood: 日常感
Audio: 脚步声，水声
SHOT_ASSETS: 人物A，人物B
            """.strip(),
        ]

        # H3 特有字段
        self.shots = [
            {
                'id': 'SH01',
                'h3_mode': 'i2va',
                'blocking_keyframe': '/path/to/keyframe1.png',
                'positioning_weight': 8,  # 站位承重高
                'appearance_weight': 2,
                'characters': ['人物A', '人物B'],
                'duration': 8
            },
            {
                'id': 'SH02',
                'h3_mode': 'ref2va',
                'asset_images': ['/path/to/asset1.png'],
                'positioning_weight': 3,  # 站位承重低
                'appearance_weight': 7,
                'characters': ['人物A', '人物B'],
                'duration': 7
            }
        ]

        # 预算
        self.zh_budget = 500
        self.zh_used = 423

        # 总时长
        self.duration = 15


# ===== 运行示例 =====

def main():
    print("=" * 70)
    print("AiFilm V2.0 - H3 项目示例")
    print("=" * 70)

    # 创建项目
    project = H3Project()

    print("\n项目信息:")
    print(f"  项目类型: H3")
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

    report = pipeline.validate(project, project_type="h3")

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

    # H3 特有检查
    print("\n" + "=" * 70)
    print("H3 模式分析:")
    print("=" * 70)

    for shot in project.shots:
        print(f"\n{shot['id']}:")
        print(f"  模式: {shot['h3_mode']}")
        print(f"  站位承重: {shot['positioning_weight']}")
        print(f"  外观承重: {shot['appearance_weight']}")

        if shot['h3_mode'] == 'i2va':
            if shot['positioning_weight'] >= 7:
                print(f"  ✅ 站位承重高，适合 i2va")
            else:
                print(f"  ⚠️  站位承重偏低，考虑 ref2va")

        elif shot['h3_mode'] == 'ref2va':
            if shot['appearance_weight'] >= 4:
                print(f"  ✅ 外观承重合理")
            else:
                print(f"  ⚠️  外观承重偏低")

    # 总结
    print("\n" + "=" * 70)
    if report['failed'] == 0:
        print("✅ H3 项目验证通过！可以继续生产。")
    else:
        print(f"❌ 项目存在 {report['failed']} 个错误，需要修复。")
    print("=" * 70)


if __name__ == "__main__":
    main()
