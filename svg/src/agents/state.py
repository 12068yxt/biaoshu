#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 工作流状态定义

Rule 5: LangGraph 状态机原则
必须使用 TypedDict，禁止随意 dict 传参
"""

import operator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, List, Optional, TypedDict, Any


# =============================================================================
# 数据模型（用于非状态字段的复杂对象）
# =============================================================================

@dataclass
class Section:
    """
    文档章节数据类
    
    Attributes:
        index: 章节序号（0-based）
        title: Heading 5 标题文本
        content: 合并后续所有正文段落（\n分隔），完整传递不截断
        hierarchy_path: 上级标题路径，如"第一章>第二节>架构设计"
    """
    index: int
    title: str
    content: str
    hierarchy_path: str

    def to_dict(self) -> dict:
        """序列化为字典（用于 JSON 报告）"""
        return {
            "index": self.index,
            "title": self.title,
            "content": self.content,
            "hierarchy_path": self.hierarchy_path,
        }


@dataclass
class SVGResult:
    """
    SVG 生成结果数据类
    
    Attributes:
        section_index: 对应章节索引
        section_title: 章节标题
        svg_content: SVG 代码内容
        svg_path: SVG 文件保存路径
        success: 是否生成成功
        error_message: 错误信息（失败时）
        timestamp: 生成时间戳（ISO 格式）
    """
    section_index: int
    section_title: str
    svg_content: str
    svg_path: str
    success: bool
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """序列化为字典（用于 JSON 报告，不含 svg_content 以减小体积）"""
        return {
            "section_index": self.section_index,
            "section_title": self.section_title,
            "svg_path": self.svg_path,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


# =============================================================================
# LangGraph 工作流状态（TypedDict）
# Rule 5: 必须使用 TypedDict，禁止随意 dict 传参
# =============================================================================

class WorkflowState(TypedDict):
    """
    LangGraph 工作流状态（TypedDict）
    
    所有字段类型化，支持 LangGraph 序列化与检查点（MemorySaver）。
    
    svg_results 使用 Annotated[List, operator.add] 实现追加语义：
    每次节点返回新的 SVGResult 列表时，自动追加到全局结果列表。
    
    Fields:
        config_path: YAML 配置文件路径
        docx_path: 输入 Word 文档路径
        thread_id: 工作流线程 ID（用于结构化日志）
        sections: 拆分后的 Section 对象列表
        split_success: 文档拆分是否成功
        split_error: 拆分错误信息
        current_section_idx: 当前绘图章节索引
        svg_results: SVG 生成结果列表（追加模式）
        output_dir: 输出根目录
        report_path: JSON 报告保存路径
        workflow_success: 工作流整体是否成功
        error_message: 全局错误信息
        config_manager: 配置管理器实例（可选，不会被序列化）
    """
    # 配置相关
    config_path: str
    # 输入文件
    docx_path: str
    # 可观测性：线程 ID 用于结构化日志
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
    # 运行时对象（不会被 LangGraph 检查点序列化）
    config_manager: Optional[Any]


def create_initial_state(
    docx_path: str,
    config_path: str = "config/standard.yaml",
    thread_id: Optional[str] = None,
) -> WorkflowState:
    """
    创建初始工作流状态
    
    Args:
        docx_path: Word 文档路径
        config_path: 配置文件路径
        thread_id: 线程 ID（可选，默认自动生成）
        
    Returns:
        初始化的 WorkflowState
    """
    if thread_id is None:
        thread_id = f"svg_workflow_{int(datetime.now().timestamp())}"
    
    return {
        "config_path": config_path,
        "docx_path": docx_path,
        "thread_id": thread_id,
        "sections": [],
        "split_success": False,
        "split_error": "",
        "current_section_idx": 0,
        "svg_results": [],
        "output_dir": "output",
        "report_path": "output/report.json",
        "workflow_success": False,
        "error_message": "",
        "config_manager": None,
    }
