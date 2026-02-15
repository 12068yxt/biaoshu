#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小标题解析测试脚本
测试七级标题（小标题）的提取功能
"""

import json
import re
from concurrent_expand import ConcurrentDocumentExpander

def test_seventh_level_titles():
    """测试七级标题提取功能"""
    print("=" * 60)
    print("七级标题（小标题）提取测试")
    print("=" * 60)
    
    # 创建扩充器实例
    expander = ConcurrentDocumentExpander()
    
    # 读取测试文档
    try:
        with open("模型架构.md", "r", encoding="utf-8") as f:
            content = f.read()
        print("✓ 成功读取模型架构.md文件")
    except FileNotFoundError:
        print("✗ 错误: 未找到 模型架构.md 文件")
        return
    
    # 测试七级标题提取
    print("\n--- 测试七级标题提取 ---")
    seventh_level_titles = expander.extract_all_seventh_level_titles(content)
    print(f"找到 {len(seventh_level_titles)} 个七级标题（小标题）")
    
    if seventh_level_titles:
        print("示例标题:")
        for i, title in enumerate(seventh_level_titles[:10], 1):  # 显示前10个
            print(f"  {i}. {title}")
        
        # 显示标题结构分析
        print("\n--- 标题结构分析 ---")
        level_distribution = {}
        for title in seventh_level_titles:
            # 统计各级别标题数量
            parts = title.split('.')[0].split('.')
            level = len(parts)
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        print("按层级分布:")
        for level, count in sorted(level_distribution.items()):
            print(f"  {level}级标题: {count} 个")
    else:
        print("未找到七级标题")
    
    # 测试不同级别的标题提取对比
    print("\n--- 多级别标题提取对比 ---")
    
    # 提取五级标题
    fifth_titles = expander.extract_all_fifth_level_titles(content)
    print(f"五级标题数量: {len(fifth_titles)}")
    
    # 提取六级标题
    sixth_titles = expander.extract_all_sixth_level_titles(content)
    print(f"六级标题数量: {len(sixth_titles)}")
    
    # 提取七级标题
    seventh_titles = expander.extract_all_seventh_level_titles(content)
    print(f"七级标题数量: {len(seventh_titles)}")
    
    # 测试配置驱动的标题提取
    print("\n--- 测试配置驱动的标题提取 ---")
    
    # 测试七级标题配置
    expander.title_level = 7
    config_titles_7 = expander.extract_all_titles(content, 7)
    print(f"配置为7级标题时提取到 {len(config_titles_7)} 个标题")
    
    # 显示一些示例
    if config_titles_7:
        print("配置驱动提取的示例标题:")
        for i, title in enumerate(config_titles_7[:5], 1):
            print(f"  {i}. {title}")
    
    # 测试配置文件读取
    print("\n--- 测试配置文件读取 ---")
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        title_level = config.get("title_settings", {}).get("title_level", 6)
        enable_subtitles = config.get("title_settings", {}).get("enable_subtitles", False)
        print(f"配置文件中设置的标题级别: {title_level}级")
        print(f"小标题功能启用状态: {enable_subtitles}")
        
        # 根据配置提取标题
        expander_from_config = ConcurrentDocumentExpander()
        config_driven_titles = expander_from_config.extract_all_titles(content)
        level_name = {5: "五级", 6: "六级", 7: "七级"}.get(expander_from_config.title_level, f"{expander_from_config.title_level}级")
        print(f"根据配置提取到 {len(config_driven_titles)} 个{level_name}标题")
        
    except FileNotFoundError:
        print("✗ 未找到配置文件 config.json")
    except json.JSONDecodeError:
        print("✗ 配置文件格式错误")
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  五级标题数量: {len(fifth_titles)}")
    print(f"  六级标题数量: {len(sixth_titles)}")
    print(f"  七级标题数量: {len(seventh_titles)}")
    print(f"  总标题数量: {len(fifth_titles) + len(sixth_titles) + len(seventh_titles)}")
    
    # 分析文档结构特点
    print("\n--- 文档结构特点分析 ---")
    if seventh_titles:
        sample_title = seventh_titles[0]
        print(f"示例七级标题: {sample_title}")
        parts = sample_title.split()[0].split('.')
        print(f"标题层级深度: {len(parts)} 层")
        print(f"完整编号结构: {'.'.join(parts)}")
    else:
        print("文档中暂无七级标题结构")

def test_subtitle_patterns():
    """测试小标题模式识别"""
    print("\n" + "=" * 60)
    print("小标题模式识别测试")
    print("=" * 60)
    
    # 测试各种可能的小标题格式
    test_cases = [
        "1.2.2.11.1.1 滑动窗口注意力机制",
        "1.2.2.11.1.2 分层位置编码设计", 
        "#### 1.2.2.11.1.3 记忆增强机制",
        "1.2.2.12.4.1 对抗样本防护机制",
        "▼ 1.2.2.11. 长文本处理与上下文扩展技术",  # 带符号的标题
        "1.2.5.1.1 教师模型选型与蒸馏环境配置（15页）"  # 带页数信息
    ]
    
    expander = ConcurrentDocumentExpander()
    
    print("测试不同格式的小标题识别:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case}")
        
        # 直接测试正则表达式
        pattern = r'^(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s+(.+)$'
        match = re.match(pattern, test_case.strip())
        if match:
            number = match.group(1)
            title_text = match.group(2)
            print(f"  ✓ 匹配成功: 编号={number}, 标题={title_text}")
        else:
            print(f"  ✗ 未匹配")
        
        # 测试完整提取函数
        dummy_content = test_case + "\n其他内容"
        extracted = expander.extract_all_seventh_level_titles(dummy_content)
        if extracted:
            print(f"  ✓ 函数提取成功: {extracted[0]}")
        else:
            print(f"  ✗ 函数提取失败")

if __name__ == "__main__":
    test_seventh_level_titles()
    test_subtitle_patterns()
    print("\n✓ 所有测试完成")