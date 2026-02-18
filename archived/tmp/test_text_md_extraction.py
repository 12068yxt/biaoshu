#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试text.md文件的标题提取
"""

from sample.concurrent_expand import ConcurrentDocumentExpander

def test_text_md_extraction():
    """测试text.md文件的标题提取"""
    print("=" * 60)
    print("text.md 标题提取测试")
    print("=" * 60)
    
    # 创建扩充器实例
    expander = ConcurrentDocumentExpander()
    
    # 读取text.md文件
    try:
        with open("text.md", "r", encoding="utf-8") as f:
            content = f.read()
        print("✓ 成功读取 text.md 文件")
        print(f"  文件大小: {len(content)} 字符")
    except FileNotFoundError:
        print("✗ 错误: 未找到 text.md 文件")
        return
    
    # 测试五级标题提取
    print("\n--- 测试五级标题提取 ---")
    fifth_level_titles = expander.extract_all_fifth_level_titles(content)
    print(f"找到 {len(fifth_level_titles)} 个五级标题")
    
    if fifth_level_titles:
        print("提取到的五级标题:")
        for i, title in enumerate(fifth_level_titles, 1):
            print(f"  {i}. {title}")
    else:
        print("未提取到任何五级标题")
        # 显示文件前几行帮助调试
        print("\n文件前10行内容:")
        lines = content.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}. {line}")
    
    # 测试六级标题提取
    print("\n--- 测试六级标题提取 ---")
    sixth_level_titles = expander.extract_all_sixth_level_titles(content)
    print(f"找到 {len(sixth_level_titles)} 个六级标题")
    
    if sixth_level_titles:
        print("提取到的六级标题:")
        for i, title in enumerate(sixth_level_titles[:10], 1):  # 只显示前10个
            print(f"  {i}. {title}")
        if len(sixth_level_titles) > 10:
            print(f"  ... 还有 {len(sixth_level_titles) - 10} 个标题")
    else:
        print("未提取到任何六级标题")

if __name__ == "__main__":
    test_text_md_extraction()