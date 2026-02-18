#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成报告节点

职责：
1. 汇总 List[SVGResult]
2. 写 JSON 报告
3. 打印统计信息
"""

import json
from datetime import datetime
from typing import Dict, Any

from ...agents.state import WorkflowState
from ...utils import register_node
from ...utils.logger import log_node_start, log_node_end, log_info


@register_node("generate_report")
def generate_report(state: WorkflowState) -> Dict[str, Any]:
    """
    生成报告节点

    Args:
        state: 工作流状态

    Returns:
        更新的状态字段字典
    """
    thread_id = state["thread_id"]
    log_node_start("generate_report", thread_id)

    try:
        # 统计信息
        svg_results = state["svg_results"]
        total = len(svg_results)
        success_count = sum(1 for r in svg_results if r.success)
        failed_count = total - success_count

        # 构建报告数据
        report = {
            "timestamp": datetime.now().isoformat(),
            "source_document": state["docx_path"],
            "statistics": {
                "total_sections": total,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": f"{success_count/total*100:.1f}%" if total > 0 else "0%"
            },
            "sections": []
        }

        # 添加章节详情
        for result in svg_results:
            report["sections"].append({
                "index": result.section_index,
                "title": result.section_title,
                "svg_path": result.svg_path,
                "success": result.success,
                "error_message": result.error_message if not result.success else "",
                "timestamp": result.timestamp
            })

        # 保存报告
        report_path = state["report_path"]
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        log_info("generate_report", thread_id, f"报告已保存: {report_path}")
        log_info("generate_report", thread_id,
                f"统计: 总计{total} | 成功{success_count} | 失败{failed_count}")
        log_node_end("generate_report", thread_id, success=True)

        return {
            "workflow_success": True,
        }

    except Exception as e:
        error_msg = f"生成报告失败: {str(e)}"
        log_node_end("generate_report", thread_id, success=False)
        log_info("generate_report", thread_id, f"错误: {error_msg}")

        return {
            "workflow_success": False,
            "error_message": error_msg,
        }
