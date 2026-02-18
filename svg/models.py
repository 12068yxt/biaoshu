#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义模块

包含：
- Section：文档章节数据类
- SVGResult：SVG生成结果数据类
- WorkflowState：LangGraph工作流状态（TypedDict，Rule 5：状态Schema类型化）

Rule 5：状态Schema必须类型化（TypedDict），禁止随意dict传参
"""

import operator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, List, Optional, TypedDict


# =============================================================================
# 文档章节数据类
# =============================================================================

@dataclass
class Section:
    """
    文档章节数据类

    Attributes:
        index: 章节序号（0-based）
        title: Heading 5标题文本
        content: 合并后续所有正文段落（\\n分隔），完整传递不截断
        hierarchy_path: 上级标题路径，如"第一章>第二节>架构设计"
    """
    index: int
    title: str
    content: str
    hierarchy_path: str

    def to_dict(self) -> dict:
        """序列化为字典（用于JSON报告）"""
        return {
            "index": self.index,
            "title": self.title,
            "content": self.content,
            "hierarchy_path": self.hierarchy_path,
        }


# =============================================================================
# SVG生成结果数据类
# =============================================================================

@dataclass
class SVGResult:
    """
    SVG生成结果数据类

    Attributes:
        section_index: 对应章节索引
        section_title: 章节标题
        svg_content: SVG代码内容
        svg_path: SVG文件保存路径
        success: 是否生成成功
        error_message: 错误信息（失败时）
        timestamp: 生成时间戳（ISO格式）
    """
    section_index: int
    section_title: str
    svg_content: str
    svg_path: str
    success: bool
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """序列化为字典（用于JSON报告，不含svg_content以减小体积）"""
        return {
            "section_index": self.section_index,
            "section_title": self.section_title,
            "svg_path": self.svg_path,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


# =============================================================================
# LangGraph工作流状态（TypedDict）
# Rule 5：必须使用TypedDict，禁止随意dict传参
# =============================================================================

class WorkflowState(TypedDict):
    """
    LangGraph工作流状态（TypedDict）

    所有字段类型化，支持LangGraph序列化与检查点（MemorySaver）。

    svg_results 使用 Annotated[List, operator.add] 实现追加语义：
    每次节点返回新的 SVGResult 列表时，自动追加到全局结果列表。

    Fields:
        config_path: YAML配置文件路径
        docx_path: 输入Word文档路径
        thread_id: 工作流线程ID（用于结构化日志）
        sections: 拆分后的Section对象列表
        split_success: 文档拆分是否成功
        split_error: 拆分错误信息
        current_section_idx: 当前绘图章节索引
        svg_results: SVG生成结果列表（追加模式）
        output_dir: 输出根目录
        report_path: JSON报告保存路径
        workflow_success: 工作流整体是否成功
        error_message: 全局错误信息
    """
    # 配置相关
    config_path: str
    # 输入文件
    docx_path: str
    # 可观测性：线程ID用于结构化日志
    thread_id: str
    # 拆分结果
    sections: List[Section]
    split_success: bool
    split_error: str
    # 绘图进度
    current_section_idx: int
    # svg_results 使用 operator.add 实现追加语义（每节点返回新项即可）
    svg_results: Annotated[List[SVGResult], operator.add]
    # 输出配置
    output_dir: str
    report_path: str
    # 最终状态
    workflow_success: bool
    error_message: str
