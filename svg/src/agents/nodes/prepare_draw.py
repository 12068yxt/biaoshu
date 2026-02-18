#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
准备绘图节点

职责：
1. 设置 current_section_idx
2. 打印进度信息
"""

from typing import Dict, Any

from ...agents.state import WorkflowState
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("prepare_draw")
def prepare_draw(state: WorkflowState) -> Dict[str, Any]:
    """
    准备绘图节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典（通常为空，因为只是日志）
    """
    thread_id = state["thread_id"]
    total = len(state["sections"])
    current = state["current_section_idx"]

    log_node_start("prepare_draw", thread_id)

    if current < total:
        section = state["sections"][current]
        log_info("prepare_draw", thread_id, f"进度: {current + 1}/{total}")
        log_info("prepare_draw", thread_id, f"当前章节: {section.title}")
        log_info("prepare_draw", thread_id, f"层级路径: {section.hierarchy_path}")

    log_node_end("prepare_draw", thread_id, success=True)

    # 此节点不修改状态，仅打印日志
    return {}
