#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单独保存TXT文件功能
"""

import os
import re
from concurrent_expand import ConcurrentDocumentExpander

def test_individual_file_saving():
    """测试单独文件保存功能"""
    print("=" * 60)
    print("单独TXT文件保存功能测试")
    print("=" * 60)
    
    # 创建测试内容
    test_title = "1.2.1.3.1.1 自注意力机制的信息聚合原理"
    test_content = """自注意力机制作为当前大语言模型架构中信息聚合过程的核心范式，
其内在原理绝非简单地对输入序列各位置进行加权求和这一表层理解所能涵盖；
它本质上是一种动态构建全局依赖关系图谱的、具有高度上下文敏感性的、
可学习的序列内关系建模方法。"""
    
    print(f"测试标题: {test_title}")
    print(f"测试内容长度: {len(test_content)} 字符")
    
    # 创建扩充器实例
    expander = ConcurrentDocumentExpander()
    
    # 测试文件保存功能
    print("\n--- 测试文件保存 ---")
    expander.save_as_individual_txt(test_title, test_content)
    
    # 验证文件是否创建成功
    expected_filename = "chapter_1.2.1.3.1.1._自注意力机制的信息聚合原理.txt"
    if os.path.exists(expected_filename):
        print(f"✓ 文件 {expected_filename} 创建成功")
        
        # 读取并验证内容
        with open(expected_filename, "r", encoding="utf-8") as f:
            saved_content = f.read()
        
        print("文件内容预览:")
        print(saved_content[:200] + "..." if len(saved_content) > 200 else saved_content)
        
        # 清理测试文件
        os.remove(expected_filename)
        print(f"✓ 测试文件已清理")
    else:
        print(f"✗ 文件 {expected_filename} 未找到")
    
    # 测试不同的标题格式
    print("\n--- 测试不同标题格式 ---")
    test_cases = [
        "1.2.5.1 基于百亿模型的数据蒸馏流程（15页）",
        "1.2.5.1.1 教师模型选型与蒸馏环境配置",
        "2.3.4.5.6.7 复杂多级标题测试",
        "无编号标题测试"
    ]
    
    for title in test_cases:
        print(f"\n测试标题: {title}")
        expander.save_as_individual_txt(title, "测试内容")
        
        # 清理生成的测试文件
        # 根据标题生成预期文件名
        if re.match(r'^\d+(?:\.\d+)*\s+.+$', title):
            number_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
            if number_match:
                number = number_match.group(1)
                title_name = number_match.group(2)
                # 清理标题名称
                clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
                clean_title = re.sub(r'_+', '_', clean_title)
                clean_title = clean_title.strip('_')
                filename = f"chapter_{number}._{clean_title}.txt"
            else:
                clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
                clean_title = re.sub(r'_+', '_', clean_title)
                filename = f"chapter_{clean_title}.txt"
        else:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clean_title = re.sub(r'_+', '_', clean_title)
            filename = f"chapter_{clean_title}.txt"
        
        if os.path.exists(filename):
            print(f"  ✓ 生成文件: {filename}")
            os.remove(filename)
            print(f"  ✓ 已清理")
        else:
            print(f"  ✗ 未找到文件: {filename}")

def show_sample_structure():
    """显示示例文件结构"""
    print("\n" + "=" * 60)
    print("示例文件命名结构")
    print("=" * 60)
    
    examples = [
        ("1.2.1.3.1.1 自注意力机制的信息聚合原理", "chapter_1.2.1.3.1.1._自注意力机制的信息聚合原理.txt"),
        ("1.2.5.1 基于百亿模型的数据蒸馏流程", "chapter_1.2.5.1._基于百亿模型的数据蒸馏流程.txt"),
        ("1.2.5.1.1 教师模型选型与蒸馏环境配置", "chapter_1.2.5.1.1._教师模型选型与蒸馏环境配置.txt")
    ]
    
    print("标题 → 文件名映射:")
    for title, filename in examples:
        print(f"  {title}")
        print(f"  ↓")
        print(f"  {filename}")
        print()

if __name__ == "__main__":
    test_individual_file_saving()
    show_sample_structure()
    print("单独文件保存功能测试完成!")