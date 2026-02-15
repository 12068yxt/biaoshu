#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标题提取功能脚本
验证五级和六级标题的提取以及配置切换功能
"""

import json
from sample.concurrent_expand import ConcurrentDocumentExpander

def test_title_extraction():
    """测试标题提取功能"""
    print("=" * 60)
    print("标题提取功能测试")
    print("=" * 60)
    
    # 创建扩充器实例
    expander = ConcurrentDocumentExpander()
    
    # 读取测试文档
    try:
        with open("工作原理.md", "r", encoding="utf-8") as f:
            content = f.read()
        print("✓ 成功读取工作原理.md文件")
    except FileNotFoundError:
        print("✗ 错误: 未找到 工作原理.md 文件")
        return
    
    # 测试六级标题提取
    print("\n--- 测试六级标题提取 ---")
    sixth_level_titles = expander.extract_all_sixth_level_titles(content)
    print(f"找到 {len(sixth_level_titles)} 个六级标题")
    if sixth_level_titles[:5]:  # 显示前5个
        print("示例标题:")
        for i, title in enumerate(sixth_level_titles[:5], 1):
            print(f"  {i}. {title}")
    else:
        print("未找到六级标题")
    
    # 测试五级标题提取
    print("\n--- 测试五级标题提取 ---")
    fifth_level_titles = expander.extract_all_fifth_level_titles(content)
    print(f"找到 {len(fifth_level_titles)} 个五级标题")
    if fifth_level_titles[:5]:  # 显示前5个
        print("示例标题:")
        for i, title in enumerate(fifth_level_titles[:5], 1):
            print(f"  {i}. {title}")
    else:
        print("未找到五级标题")
    
    # 测试配置驱动的标题提取
    print("\n--- 测试配置驱动的标题提取 ---")
    
    # 测试六级标题配置
    expander.title_level = 6
    config_titles_6 = expander.extract_all_titles(content, 6)
    print(f"配置为6级标题时提取到 {len(config_titles_6)} 个标题")
    
    # 测试五级标题配置
    expander.title_level = 5
    config_titles_5 = expander.extract_all_titles(content, 5)
    print(f"配置为5级标题时提取到 {len(config_titles_5)} 个标题")
    
    # 测试配置文件读取
    print("\n--- 测试配置文件读取 ---")
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        title_level = config.get("title_settings", {}).get("title_level", 6)
        print(f"配置文件中设置的标题级别: {title_level}级")
        
        # 根据配置提取标题
        expander_from_config = ConcurrentDocumentExpander()
        config_driven_titles = expander_from_config.extract_all_titles(content)
        level_name = "五级" if expander_from_config.title_level == 5 else "六级"
        print(f"根据配置提取到 {len(config_driven_titles)} 个{level_name}标题")
        
    except FileNotFoundError:
        print("✗ 未找到配置文件 config.json")
    except json.JSONDecodeError:
        print("✗ 配置文件格式错误")
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  六级标题数量: {len(sixth_level_titles)}")
    print(f"  五级标题数量: {len(fifth_level_titles)}")
    print(f"  当前配置级别: {expander.title_level}级")
    print("=" * 60)

def test_error_handling():
    """测试错误处理功能"""
    print("\n" + "=" * 60)
    print("错误处理功能测试")
    print("=" * 60)
    
    expander = ConcurrentDocumentExpander()
    
    # 测试无效级别
    try:
        invalid_titles = expander.extract_all_titles("test content", 4)
        print("✗ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✓ 正确处理无效级别: {e}")
    
    # 测试空内容
    empty_titles = expander.extract_all_titles("", 6)
    print(f"✓ 空内容处理: 返回 {len(empty_titles)} 个标题")
    
    print("=" * 60)

if __name__ == "__main__":
    test_title_extraction()
    test_error_handling()
    print("\n所有测试完成!")