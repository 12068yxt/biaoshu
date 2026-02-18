#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 图结构可视化导出

Rule 6: 状态可观测原则
LangGraph 图结构可视化导出（Mermaid 或 PNG）
"""

from typing import Optional


def export_mermaid(workflow, output_path: str = "output/workflow_graph.md") -> str:
    """
    导出工作流图为 Mermaid 格式

    Args:
        workflow: LangGraph 编译后的工作流
        output_path: 输出文件路径

    Returns:
        Mermaid 图代码
    """
    # 获取图的内部结构
    graph = workflow.get_graph()

    # 生成 Mermaid 代码
    mermaid_code = graph.draw_mermaid()

    # 保存到文件
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# SVG 工作流图\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")

    return mermaid_code


def export_png(workflow, output_path: str = "output/workflow_graph.png") -> str:
    """
    导出工作流图为 PNG 格式

    需要安装: pip install pillow

    Args:
        workflow: LangGraph 编译后的工作流
        output_path: 输出文件路径

    Returns:
        输出文件路径
    """
    try:
        from PIL import Image
        import io

        # 获取 PNG 数据
        png_data = workflow.get_graph().draw_png()

        # 保存到文件
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(png_data)

        return output_path

    except ImportError:
        raise ImportError("导出 PNG 需要安装 pillow: pip install pillow")
