#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG 绘图节点

职责：
1. 使用 SmartDrawer 获取提示词
2. 调用 LLM 生成 SVG
3. 验证保存 SVG
4. 记录结果
"""

from typing import Dict, Any, List

from ...agents.state import WorkflowState, SVGResult
from ...tools import SmartDrawer
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("draw_svg")
def draw_svg(state: WorkflowState) -> Dict[str, Any]:
    """
    SVG 绘图节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典（包含 svg_results 列表）
    """
    thread_id = state["thread_id"]
    current_idx = state["current_section_idx"]
    sections = state["sections"]

    # 如果已经处理完所有章节，直接返回
    if current_idx >= len(sections):
        return {"svg_results": []}

    section = sections[current_idx]
    log_node_start("draw_svg", thread_id)
    log_info("draw_svg", thread_id, f"正在生成: {section.title}")

    try:
        # 获取配置管理器
        config_manager = state["config_manager"]

        # 创建智能绘图器
        drawer = SmartDrawer(config_manager)

        # 获取 SVG 输出目录
        output_config = config_manager.get_output_config()
        svg_dir = output_config.get('svg_dir', 'output/svgs')

        # 生成 SVG
        result = drawer.draw(section, svg_dir)

        if result.success:
            log_info("draw_svg", thread_id, f"成功: {result.svg_path}")
            log_node_end("draw_svg", thread_id, success=True)
        else:
            log_info("draw_svg", thread_id, f"失败（使用备用）: {result.error_message}")
            log_node_end("draw_svg", thread_id, success=False)

        # 返回结果列表（LangGraph 会自动追加）
        return {"svg_results": [result]}

    except Exception as e:
        error_msg = str(e)
        log_node_end("draw_svg", thread_id, success=False)
        log_info("draw_svg", thread_id, f"错误: {error_msg}")

        # 记录失败结果
        error_result = SVGResult(
            section_index=section.index,
            section_title=section.title,
            svg_content="",
            svg_path="",
            success=False,
            error_message=error_msg
        )

        return {"svg_results": [error_result]}
