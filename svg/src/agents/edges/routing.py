#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
条件边路由模块

Rule 7: 条件边逻辑独立文件

包含：
- check_split_result: 拆分结果检查
- check_continue: 继续检查（循环或完成）
"""

from ...agents.state import WorkflowState
from ...utils.logger import log_decision


def check_split_result(state: WorkflowState) -> str:
    """
    拆分结果检查条件

    条件分支：
    - 成功→"prepare_draw"
    - 失败/空→"handle_error"

    Args:
        state: 工作流状态

    Returns:
        下一个节点名称
    """
    thread_id = state["thread_id"]

    if state["split_success"] and len(state["sections"]) > 0:
        log_decision("check_split_result", thread_id, "成功", "继续到 prepare_draw")
        return "prepare_draw"
    else:
        log_decision("check_split_result", thread_id, "失败", "跳转到 handle_error")
        return "handle_error"


def check_continue(state: WorkflowState) -> str:
    """
    继续检查条件

    条件分支：
    - 还有章节→"prepare_draw"（循环）
    - 全部完成→"generate_report"

    Args:
        state: 工作流状态

    Returns:
        下一个节点名称
    """
    thread_id = state["thread_id"]
    current_idx = state["current_section_idx"]
    total = len(state["sections"])

    # current_idx 已经在 draw_svg 节点递增
    if current_idx < total:
        log_decision("check_continue", thread_id, "继续循环",
                    f"进度 {current_idx + 1}/{total}")
        return "prepare_draw"
    else:
        log_decision("check_continue", thread_id, "全部完成",
                    f"共处理 {total} 个章节")
        return "generate_report"
