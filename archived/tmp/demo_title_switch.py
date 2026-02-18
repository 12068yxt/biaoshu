#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题级别切换演示脚本
展示如何在五级和六级标题之间切换处理模式
"""

import json
import shutil
from datetime import datetime

def switch_title_level(level: int):
    """切换标题处理级别"""
    if level not in [5, 6]:
        raise ValueError("标题级别只能是5或6")
    
    # 备份当前配置
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("未找到配置文件，创建默认配置...")
        config = {
            "api_settings": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 300,
                "concurrent_limit": 3
            },
            "title_settings": {
                "title_level": 6
            }
        }
    
    # 更新标题级别
    old_level = config.get("title_settings", {}).get("title_level", 6)
    config.setdefault("title_settings", {})["title_level"] = level
    
    # 保存配置
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    level_names = {5: "五级", 6: "六级"}
    print(f"✓ 标题级别已从 {level_names[old_level]} 切换到 {level_names[level]}")
    return old_level

def show_current_configuration():
    """显示当前配置"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        title_level = config.get("title_settings", {}).get("title_level", 6)
        level_names = {5: "五级标题", 6: "六级标题"}
        
        print("当前配置:")
        print(f"  标题处理级别: {title_level}级 ({level_names[title_level]})")
        print(f"  API超时时间: {config['api_settings']['timeout']}秒")
        print(f"  并发限制: {config['api_settings']['concurrent_limit']}个请求")
        
        return title_level
    except FileNotFoundError:
        print("✗ 未找到配置文件 config.json")
        return None

def demonstrate_switching():
    """演示标题级别切换"""
    print("=" * 60)
    print("标题处理级别切换演示")
    print("=" * 60)
    
    # 显示当前配置
    print("\n1. 当前配置状态:")
    current_level = show_current_configuration()
    
    if current_level is None:
        return
    
    # 演示切换到五级标题
    print("\n2. 切换到五级标题处理:")
    if current_level != 5:
        old_level = switch_title_level(5)
        show_current_configuration()
    else:
        print("  ✓ 已经是五级标题处理模式")
    
    # 演示切换到六级标题
    print("\n3. 切换到六级标题处理:")
    if current_level != 6:
        switch_title_level(6)
        show_current_configuration()
    else:
        print("  ✓ 已经是六级标题处理模式")
    
    # 恢复原始配置
    print("\n4. 恢复原始配置:")
    switch_title_level(current_level)
    show_current_configuration()
    
    print("\n" + "=" * 60)
    print("演示完成!")

def show_document_statistics():
    """显示文档标题统计信息"""
    print("\n" + "=" * 60)
    print("文档标题统计信息")
    print("=" * 60)
    
    try:
        from sample.concurrent_expand import ConcurrentDocumentExpander
        expander = ConcurrentDocumentExpander()
        
        with open("工作原理.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 统计各级别标题
        fifth_titles = expander.extract_all_fifth_level_titles(content)
        sixth_titles = expander.extract_all_sixth_level_titles(content)
        
        print(f"文档统计:")
        print(f"  五级标题数量: {len(fifth_titles)}")
        print(f"  六级标题数量: {len(sixth_titles)}")
        print(f"  总标题数量: {len(fifth_titles) + len(sixth_titles)}")
        
        if fifth_titles:
            print(f"\n五级标题示例:")
            for i, title in enumerate(fifth_titles[:3], 1):
                print(f"  {i}. {title}")
        
        if sixth_titles:
            print(f"\n六级标题示例:")
            for i, title in enumerate(sixth_titles[:3], 1):
                print(f"  {i}. {title}")
                
    except Exception as e:
        print(f"✗ 统计失败: {e}")

if __name__ == "__main__":
    demonstrate_switching()
    show_document_statistics()