#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 工作流图构建

Rule 7: 图构建入口（仅负责组装，不包含业务逻辑）
图结构代码 ≤200 行
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import WorkflowState
from .nodes import (
    initialize, split_document, prepare_draw,
    draw_svg, generate_report, handle_error,
)
from .edges import check_split_result, check_continue


def build_workflow() -> StateGraph:
    """
    构建 LangGraph 工作流

    工作流图结构：

                    ┌─────────────┐
                    │ initialize  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │split_document│
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐
    │  check_split    │      │   handle_error  │
    │  (条件检查)      │      │   (错误处理)     │
    └────────┬────────┘      └─────────────────┘
             │ 成功
             ▼
    ┌─────────────────┐
    │  prepare_draw   │◄────────────────┐
    │  (准备绘图)      │                 │
    └────────┬────────┘                 │
             │                          │
             ▼                          │
    ┌─────────────────┐                 │
    │    draw_svg     │                 │
    │  (智能绘图)      │                 │
    └────────┬────────┘                 │
             │                          │
             ▼                          │
    ┌─────────────────┐                 │
    │  check_continue │─────────────────┘
    │  (继续检查)      │（还有章节）
    └────────┬────────┘
             │ 完成
             ▼
    ┌─────────────────┐
    │ generate_report │
    │   (生成报告)     │
    └─────────────────┘

    Returns:
        编译后的 StateGraph
    """
    # 创建工作流图
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("initialize", initialize)
    workflow.add_node("split_document", split_document)
    workflow.add_node("prepare_draw", prepare_draw)
    workflow.add_node("draw_svg", draw_svg)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("handle_error", handle_error)

    # 设置入口节点
    workflow.set_entry_point("initialize")

    # 添加边
    workflow.add_edge("initialize", "split_document")

    # 条件分支：拆分结果检查
    workflow.add_conditional_edges(
        "split_document",
        check_split_result,
        {
            "prepare_draw": "prepare_draw",
            "handle_error": "handle_error"
        }
    )

    # 准备绘图 -> 智能绘图
    workflow.add_edge("prepare_draw", "draw_svg")

    # 条件分支：继续检查（循环或完成）
    workflow.add_conditional_edges(
        "draw_svg",
        check_continue,
        {
            "prepare_draw": "prepare_draw",
            "generate_report": "generate_report"
        }
    )

    # 结束节点
    workflow.add_edge("generate_report", END)
    workflow.add_edge("handle_error", END)

    # 编译工作流（使用内存检查点）
    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)

    return compiled_workflow
