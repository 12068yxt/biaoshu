#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档拆分节点

职责：
1. 使用 DocumentSplitter 解析 docx
2. 按 Heading 5 拆分章节
3. 输出 List[Section]
"""

from typing import Dict, Any

from ...agents.state import WorkflowState
from ...tools import DocumentSplitter
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("split_document")
def split_document(state: WorkflowState) -> Dict[str, Any]:
    """
    文档拆分节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典
    """
    thread_id = state["thread_id"]
    docx_path = state["docx_path"]

    log_node_start("split_document", thread_id)
    log_info("split_document", thread_id, f"开始解析文档: {docx_path}")

    try:
        # 创建文档拆分器
        splitter = DocumentSplitter(docx_path)

        # 拆分文档
        sections = splitter.split_by_heading5()

        split_success = len(sections) > 0
        split_error = "" if split_success else "未找到Heading 5章节"

        log_info("split_document", thread_id, f"成功拆分 {len(sections)} 个章节")
        for section in sections:
            log_info("split_document", thread_id,
                    f"[{section.index}] {section.title} (路径: {section.hierarchy_path})")

        log_node_end("split_document", thread_id, success=split_success)

        return {
            "sections": sections,
            "split_success": split_success,
            "split_error": split_error,
        }

    except Exception as e:
        error_msg = str(e)
        log_node_end("split_document", thread_id, success=False)
        log_info("split_document", thread_id, f"错误: {error_msg}")

        return {
            "sections": [],
            "split_success": False,
            "split_error": error_msg,
        }
