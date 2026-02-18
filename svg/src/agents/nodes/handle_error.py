#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理节点

职责：
1. 记录错误信息
2. 优雅退出
"""

from typing import Dict, Any

from ...agents.state import WorkflowState
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("handle_error")
def handle_error(state: WorkflowState) -> Dict[str, Any]:
    """
    错误处理节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典
    """
    thread_id = state["thread_id"]
    log_node_start("handle_error", thread_id)

    # 确定错误信息
    if state["split_error"]:
        error_message = f"文档拆分错误: {state['split_error']}"
    elif state["error_message"]:
        error_message = state["error_message"]
    else:
        error_message = "未知错误"

    log_info("handle_error", thread_id, f"错误信息: {error_message}")
    log_info("handle_error", thread_id, "工作流已终止")
    log_node_end("handle_error", thread_id, success=False)

    return {
        "workflow_success": False,
        "error_message": error_message,
    }
