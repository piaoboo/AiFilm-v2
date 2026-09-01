#!/usr/bin/env python3
"""
Seedance 2.5 适配器

将项目数据转换为 Seedance 2.5 API 格式

版本: v0.1.0
日期: 2026-09-01
"""

from typing import Dict, Any, List


class SeedanceAdapter:
    """
    Seedance 2.5 适配器

    负责：
    1. 数据格式转换
    2. API 参数生成
    3. 时长限制（30s）
    4. 八段格式化
    """

    MAX_DURATION = 30  # Seedance 单镜最长 30s

    def __init__(self):
        self.api_version = "2.5"

    def format_prompt(self, shot: Dict[str, Any]) -> str:
        """
        格式化单个镜头的 prompt

        Args:
            shot: 镜头数据

        Returns:
            格式化的 prompt 字符串
        """
        sections = []

        # SHOT_META
        if shot.get('meta'):
            sections.append(f"SHOT_META: {shot['meta']}")

        # Dynamic
        if shot.get('dynamic'):
            sections.append(f"Dynamic: {shot['dynamic']}")

        # Static
        if shot.get('static'):
            sections.append(f"Static: {shot['static']}")

        # Camera
        if shot.get('camera'):
            sections.append(f"Camera: {shot['camera']}")

        # Optics
        if shot.get('optics'):
            sections.append(f"Optics: {shot['optics']}")

        # Style & Mood
        if shot.get('style'):
            sections.append(f"Style & Mood: {shot['style']}")

        # Audio
        if shot.get('audio'):
            sections.append(f"Audio: {shot['audio']}")

        # SHOT_ASSETS
        if shot.get('assets'):
            sections.append(f"SHOT_ASSETS: {shot['assets']}")

        return "\n".join(sections)

    def validate_duration(self, duration: float) -> bool:
        """验证时长是否符合 Seedance 限制"""
        return 0 < duration <= self.MAX_DURATION

    def convert_project(self, project: Any) -> Dict[str, Any]:
        """
        转换整个项目为 Seedance 格式

        Args:
            project: 项目数据

        Returns:
            Seedance API 格式的数据
        """
        shots = []

        for shot in getattr(project, 'shots', []):
            formatted = {
                'id': shot.get('id'),
                'prompt': self.format_prompt(shot),
                'duration': shot.get('duration', 5),
            }
            shots.append(formatted)

        return {
            'api_version': self.api_version,
            'shots': shots,
            'total_duration': sum(s['duration'] for s in shots)
        }


if __name__ == "__main__":
    print("Seedance 适配器测试")

    adapter = SeedanceAdapter()

    # 测试 prompt 格式化
    shot = {
        'id': 'SH01',
        'meta': '镜1',
        'dynamic': '侦探推开车门',
        'static': '城市街道',
        'camera': '跟镜',
        'duration': 5
    }

    prompt = adapter.format_prompt(shot)
    print(f"\n格式化 prompt:\n{prompt}")

    # 测试时长验证
    print(f"\n时长验证:")
    print(f"  5s: {adapter.validate_duration(5)}")
    print(f"  30s: {adapter.validate_duration(30)}")
    print(f"  35s: {adapter.validate_duration(35)}")
