#!/usr/bin/env python3
"""
V1 兼容层

提供 AiFilm-pipeline (V1) 到 AiFilm-v2 (V2) 的兼容接口。

核心功能：
1. 将 V1 的 _data.py 转换为 V2 的 Model
2. 支持混合模式（V1 + V2 规则共存）
3. 提供平滑迁移路径

版本: v0.1.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加 core 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import Pipeline, RuleEngine


class V1Adapter:
    """
    V1 兼容适配器

    负责：
    1. V1 数据格式转换
    2. V1 规则包装
    3. 混合模式支持
    """

    def __init__(self):
        self.pipeline = Pipeline()
        self.v1_mode = False  # 是否启用 V1 兼容模式

    def load_v1_data(self, data_path: str) -> Any:
        """
        加载 V1 的 _data.py 文件

        Args:
            data_path: _data.py 文件路径

        Returns:
            V1 数据模型对象
        """
        # 动态导入 V1 数据文件
        import importlib.util
        spec = importlib.util.spec_from_file_location("v1_data", data_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"无法加载 V1 数据文件: {data_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # V1 数据通常导出一个 Model 类实例
        return getattr(module, 'Model', module)

    def convert_v1_to_v2(self, v1_model: Any) -> Dict[str, Any]:
        """
        将 V1 模型转换为 V2 格式

        Args:
            v1_model: V1 数据模型

        Returns:
            V2 格式的数据字典
        """
        v2_data = {
            'project_type': 'seedance',  # 默认 Seedance
            'shots': [],
            'metadata': {}
        }

        # 提取基本信息
        v2_data['metadata'] = {
            'n_sub': getattr(v1_model, 'n_sub', 0),
            'n_sb': getattr(v1_model, 'n_sb', 0),
            'n_vid': getattr(v1_model, 'n_vid', 0),
            'n_sty': getattr(v1_model, 'n_sty', 0),
            'n_anc': getattr(v1_model, 'n_anc', 0),
        }

        # 提取镜头数据
        # V1 通常将镜头存储在 SU01, SU02 等属性中
        for attr_name in dir(v1_model):
            if attr_name.startswith('SU'):
                su = getattr(v1_model, attr_name)
                # 提取子单元的镜头
                if hasattr(su, 'shots'):
                    for shot in su.shots:
                        v2_shot = self._convert_shot(shot)
                        v2_data['shots'].append(v2_shot)

        return v2_data

    def _convert_shot(self, v1_shot: Any) -> Dict[str, Any]:
        """
        转换单个镜头

        Args:
            v1_shot: V1 镜头数据

        Returns:
            V2 格式的镜头字典
        """
        return {
            'id': getattr(v1_shot, 'id', ''),
            'meta': getattr(v1_shot, 'meta', ''),
            'dynamic': getattr(v1_shot, 'dynamic', ''),
            'static': getattr(v1_shot, 'static', ''),
            'camera': getattr(v1_shot, 'camera', ''),
            'optics': getattr(v1_shot, 'optics', ''),
            'style': getattr(v1_shot, 'style', ''),
            'audio': getattr(v1_shot, 'audio', ''),
            'assets': getattr(v1_shot, 'assets', ''),
            'duration': getattr(v1_shot, 'duration', 5),
        }

    def validate_v1_project(self, data_path: str) -> Dict[str, Any]:
        """
        使用 V2 规则验证 V1 项目

        Args:
            data_path: V1 数据文件路径

        Returns:
            验证报告
        """
        # 加载 V1 数据
        v1_model = self.load_v1_data(data_path)

        # 直接使用 V1 模型进行验证（V2 规则兼容 V1 数据结构）
        report = self.pipeline.validate(v1_model, project_type='seedance')

        return report

    def migrate_v1_to_v2(
        self,
        v1_data_path: str,
        v2_output_path: str
    ) -> Dict[str, Any]:
        """
        迁移 V1 项目到 V2 格式

        Args:
            v1_data_path: V1 数据文件路径
            v2_output_path: V2 输出路径

        Returns:
            迁移报告
        """
        # 加载 V1 数据
        v1_model = self.load_v1_data(v1_data_path)

        # 转换为 V2 格式
        v2_data = self.convert_v1_to_v2(v1_model)

        # 保存 V2 数据
        import json
        with open(v2_output_path, 'w', encoding='utf-8') as f:
            json.dump(v2_data, f, ensure_ascii=False, indent=2)

        return {
            'success': True,
            'v1_path': v1_data_path,
            'v2_path': v2_output_path,
            'shots_migrated': len(v2_data['shots']),
            'metadata': v2_data['metadata']
        }


class MixedModeRunner:
    """
    混合模式运行器

    支持 V1 和 V2 规则同时运行
    """

    def __init__(self):
        self.v1_adapter = V1Adapter()
        self.v2_pipeline = Pipeline()

    def run_mixed_validation(
        self,
        v1_model: Any,
        use_v1_rules: bool = True,
        use_v2_rules: bool = True
    ) -> Dict[str, Any]:
        """
        混合模式验证

        Args:
            v1_model: V1 数据模型
            use_v1_rules: 是否使用 V1 规则
            use_v2_rules: 是否使用 V2 规则

        Returns:
            合并的验证报告
        """
        report = {
            'v1_results': None,
            'v2_results': None,
            'combined': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }

        # V1 规则（如果需要）
        if use_v1_rules:
            # 这里可以调用原有的 validators.py
            # 暂时跳过
            pass

        # V2 规则
        if use_v2_rules:
            v2_report = self.v2_pipeline.validate(v1_model, project_type='seedance')
            report['v2_results'] = v2_report
            report['combined']['total'] += v2_report['total']
            report['combined']['passed'] += v2_report['passed']
            report['combined']['failed'] += v2_report['failed']
            report['combined']['warnings'] += v2_report['warnings']

        return report


if __name__ == "__main__":
    print("=" * 60)
    print("V1 兼容层测试")
    print("=" * 60)

    adapter = V1Adapter()

    # 测试数据转换
    class MockV1Model:
        n_sub = 5
        n_sb = 5
        n_vid = 5
        n_sty = 5
        n_anc = 5

        class SU01:
            shots = [
                {'id': 'SH01', 'dynamic': '测试动作', 'duration': 5}
            ]

    v1_model = MockV1Model()
    v1_model.SU01 = MockV1Model.SU01()

    v2_data = adapter.convert_v1_to_v2(v1_model)

    print(f"\nV1→V2 转换:")
    print(f"  元数据: {v2_data['metadata']}")
    print(f"  镜头数: {len(v2_data['shots'])}")
    print(f"  第一镜: {v2_data['shots'][0] if v2_data['shots'] else 'None'}")

    print("\n" + "=" * 60)
