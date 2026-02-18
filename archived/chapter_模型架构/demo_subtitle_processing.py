#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小标题处理演示脚本
展示如何解析和生成小标题内容
"""

import asyncio
import aiohttp
import os
import re
from concurrent_expand import ConcurrentDocumentExpander

async def demo_subtitle_processing():
    """演示小标题处理功能"""
    print("=" * 60)
    print("小标题处理功能演示")
    print("=" * 60)
    
    # 初始化扩充器
    expander = ConcurrentDocumentExpander()
    
    # 读取文档
    try:
        with open("模型架构.md", "r", encoding="utf-8") as f:
            content = f.read()
        print("✓ 成功读取模型架构.md")
    except Exception as e:
        print(f"✗ 读取文档失败: {e}")
        return
    
    # 提取标题
    print("\n--- 标题提取结果 ---")
    fifth_titles = expander.extract_all_fifth_level_titles(content)
    sixth_titles = expander.extract_all_sixth_level_titles(content)
    
    print(f"五级标题数量: {len(fifth_titles)}")
    print(f"六级标题数量: {len(sixth_titles)}")
    
    # 显示示例
    if fifth_titles:
        print("\n五级标题示例:")
        for i, title in enumerate(fifth_titles[:3], 1):
            print(f"  {i}. {title}")
    
    if sixth_titles:
        print("\n六级标题示例:")
        for i, title in enumerate(sixth_titles[:5], 1):
            print(f"  {i}. {title}")
    
    # 演示内容生成（使用第一个六级标题作为示例）
    if sixth_titles:
        sample_title = sixth_titles[0]
        print(f"\n--- 内容生成演示 ---")
        print(f"处理标题: {sample_title}")
        
        # 检查API密钥
        api_key = os.getenv("ALIYUN_API_KEY")
        if not api_key:
            print("⚠️  未设置 ALIYUN_API_KEY 环境变量，跳过API调用演示")
            print("请设置: export ALIYUN_API_KEY='your_api_key'")
            return
        
        # 创建提示词
        prompt = expander.create_prompt(sample_title)
        print(f"提示词长度: {len(prompt)} 字符")
        
        # 演示文件保存功能
        print("\n--- 文件保存演示 ---")
        test_content = f"这是关于'{sample_title}'的测试内容。\n\n详细技术说明内容..."
        
        # 保存到主文件
        expander.append_to_markdown_file(sample_title, test_content, "模型架构_expanded.md")
        
        # 保存为独立文件
        expander.save_as_individual_md(sample_title, test_content)
        
        print("✓ 文件保存演示完成")
        
        # 演示API调用（如果需要的话）
        print("\n--- API调用准备 ---")
        print("如需实际生成内容，请运行:")
        print("python concurrent_expand.py")
        
    else:
        print("\n⚠️  未找到可处理的标题")

def show_document_structure():
    """显示文档结构分析"""
    print("\n" + "=" * 60)
    print("文档结构分析")
    print("=" * 60)
    
    try:
        with open("模型架构.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 统计各级标题
        level_counts = {"五级": 0, "六级": 0, "其他": 0}
        
        for line in lines:
            line = line.strip()
            if line.startswith("## ▼"):
                level_counts["五级"] += 1
            elif line.startswith("### "):
                level_counts["六级"] += 1
            elif line.startswith("## ") and not line.startswith("## ▼"):
                level_counts["其他"] += 1
        
        print("标题层级统计:")
        for level, count in level_counts.items():
            print(f"  {level}标题: {count} 个")
        
        print(f"\n总行数: {len(lines)}")
        
        # 显示文档片段
        print("\n文档开头片段:")
        for i, line in enumerate(lines[:10]):
            if line.strip():
                print(f"  {i+1:2d}. {line.rstrip()}")
                
    except Exception as e:
        print(f"✗ 分析文档结构时出错: {e}")

if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_subtitle_processing())
    show_document_structure()
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)