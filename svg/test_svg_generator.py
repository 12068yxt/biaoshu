#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG生成器测试脚本
演示基本功能和使用方法
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from ppt_svg_generator import PPTSVGGenerator

def test_prompt_generation():
    """测试提示词生成功能"""
    print("=== 测试提示词生成 ===")
    
    generator = PPTSVGGenerator()
    
    # 测试内容
    test_cases = [
        {
            "title": "自注意力机制流程",
            "content": "自注意力机制包括查询向量、键向量、值向量的计算，相似度计算，Softmax归一化，加权求和等核心步骤。",
            "expected_type": "flowchart"
        },
        {
            "title": "Transformer架构",
            "content": "Transformer模型包含编码器-解码器结构，多头注意力机制，前馈神经网络，残差连接和层归一化等组件。",
            "expected_type": "architecture"
        },
        {
            "title": "数据处理流水线",
            "content": "数据从输入源经过预处理、特征提取、模型推理、后处理等步骤，最终输出结果。",
            "expected_type": "data_flow"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"标题: {case['title']}")
        print(f"预期类型: {case['expected_type']}")
        
        # 自动选择图表类型
        diagram_type = generator.select_diagram_type(case['title'], case['content'])
        print(f"实际选择类型: {diagram_type}")
        
        # 生成提示词
        prompt = generator.generate_prompt(diagram_type, case['title'], case['content'])
        print(f"提示词长度: {len(prompt)} 字符")
        print("-" * 50)

def test_chapter_processing():
    """测试章节文件处理"""
    print("\n=== 测试章节文件处理 ===")
    
    generator = PPTSVGGenerator()
    
    # 查找测试文件
    chapter_dir = Path("../chapter_1.2.1.3")
    if not chapter_dir.exists():
        print("章节目录不存在，跳过测试")
        return
    
    txt_files = list(chapter_dir.glob("*.txt"))[:2]  # 只测试前2个文件
    
    for file_path in txt_files:
        print(f"\n处理文件: {file_path.name}")
        
        # 提取信息
        title, chapter_id = generator.extract_chapter_info(file_path.name)
        print(f"提取标题: {title}")
        print(f"章节ID: {chapter_id}")
        
        # 读取内容
        content = generator.read_chapter_content(file_path)
        print(f"内容长度: {len(content)} 字符")
        
        if content:
            # 选择图表类型
            diagram_type = generator.select_diagram_type(title, content)
            print(f"选择图表类型: {diagram_type}")

def main():
    """主测试函数"""
    print("SVG生成器功能测试")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv('ALIYUN_API_KEY')
    if not api_key:
        print("警告: 未设置 ALIYUN_API_KEY 环境变量")
        print("某些功能可能无法正常工作")
    else:
        print("API密钥已设置")
    
    # 运行测试
    test_prompt_generation()
    test_chapter_processing()
    
    print("\n=== 测试完成 ===")
    print("\n接下来可以运行以下命令进行实际生成:")
    print("python ppt_svg_generator.py --mode debug  # 调试模式")
    print("python ppt_svg_generator.py --mode batch  # 批量生成")

if __name__ == "__main__":
    main()