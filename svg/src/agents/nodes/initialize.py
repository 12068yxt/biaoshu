#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化节点

职责：
1. 加载配置，创建 ConfigManager
2. 创建输出目录
3. 初始化状态
"""

import os
from typing import Dict, Any

from ...agents.state import WorkflowState
from ...config import ConfigManager
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("initialize")
def initialize(state: WorkflowState) -> Dict[str, Any]:
    """
    初始化节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典
    """
    thread_id = state["thread_id"]
    log_node_start("initialize", thread_id)

    try:
        # 创建配置管理器
        config_manager = ConfigManager(state["config_path"])

        # 获取输出配置
        output_config = config_manager.get_output_config()
        output_dir = os.path.dirname(output_config.get('report_file', 'output/report.json'))
        svg_dir = output_config.get('svg_dir', 'output/svgs')
        report_path = output_config.get('report_file', 'output/report.json')

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(svg_dir, exist_ok=True)

        log_info("initialize", thread_id, f"配置加载成功: {state['config_path']}")
        log_info("initialize", thread_id, f"输出目录: {output_dir}")
        log_info("initialize", thread_id, f"SVG目录: {svg_dir}")
        log_node_end("initialize", thread_id, success=True)

        return {
            "config_manager": config_manager,
            "output_dir": output_dir,
            "report_path": report_path,
        }

    except Exception as e:
        log_node_end("initialize", thread_id, success=False)
        return {
            "workflow_success": False,
            "error_message": f"初始化失败: {str(e)}",
        }
