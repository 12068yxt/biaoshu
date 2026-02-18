#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结构化日志模块

Rule 6: 状态可观测原则
每步状态变更打印结构化日志（含 thread_id 与 node_name）
"""

from typing import Optional
from datetime import datetime


def log_node_start(node_name: str, thread_id: str) -> None:
    """记录节点开始执行"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [thread:{thread_id}] [node:{node_name}] ▶️ 开始执行")


def log_node_end(node_name: str, thread_id: str, success: bool = True) -> None:
    """记录节点执行完成"""
    timestamp = datetime.now().isoformat()
    status = "✅ 成功" if success else "❌ 失败"
    print(f"[{timestamp}] [thread:{thread_id}] [node:{node_name}] {status} 执行完成")


def log_node_error(node_name: str, thread_id: str, error: str) -> None:
    """记录节点执行错误"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [thread:{thread_id}] [node:{node_name}] ❌ 错误: {error}")


def log_info(node_name: str, thread_id: str, message: str) -> None:
    """记录一般信息"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [thread:{thread_id}] [node:{node_name}] ℹ️ {message}")


def log_decision(node_name: str, thread_id: str, decision: str, details: Optional[str] = None) -> None:
    """记录关键决策节点（工具调用、LLM 输出）"""
    timestamp = datetime.now().isoformat()
    detail_str = f" ({details})" if details else ""
    print(f"[{timestamp}] [thread:{thread_id}] [node:{node_name}] 🔀 决策: {decision}{detail_str}")
