#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册装饰器模块

提供 @register_tool 和 @register_node 装饰器，实现显式注册机制。
禁止自动扫描或魔法 import。

Rule 7: 显式注册机制
"""

from typing import Callable, Dict, Any
from functools import wraps

# 全局注册表
_tool_registry: Dict[str, Callable] = {}
_node_registry: Dict[str, Callable] = {}


def register_tool(name: str) -> Callable:
    """
    工具注册装饰器
    
    Args:
        name: 工具名称
        
    Example:
        @register_tool("document_splitter")
        def split_document(...) -> ...:
            ...
    """
    def decorator(func: Callable) -> Callable:
        _tool_registry[name] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 附加元数据
        wrapper._registered_name = name
        wrapper._is_tool = True
        return wrapper
    return decorator


def register_node(name: str) -> Callable:
    """
    节点注册装饰器
    
    Args:
        name: 节点名称
        
    Example:
        @register_node("initialize")
        def initialize_node(state: WorkflowState) -> WorkflowState:
            ...
    """
    def decorator(func: Callable) -> Callable:
        _node_registry[name] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 附加元数据
        wrapper._registered_name = name
        wrapper._is_node = True
        return wrapper
    return decorator


def get_tool(name: str) -> Callable:
    """获取已注册的工具"""
    if name not in _tool_registry:
        raise KeyError(f"工具未注册: {name}")
    return _tool_registry[name]


def get_node(name: str) -> Callable:
    """获取已注册的节点"""
    if name not in _node_registry:
        raise KeyError(f"节点未注册: {name}")
    return _node_registry[name]


def list_tools() -> Dict[str, Callable]:
    """列出所有已注册的工具"""
    return _tool_registry.copy()


def list_nodes() -> Dict[str, Callable]:
    """列出所有已注册的节点"""
    return _node_registry.copy()


def clear_registry():
    """清空注册表（用于测试）"""
    _tool_registry.clear()
    _node_registry.clear()
