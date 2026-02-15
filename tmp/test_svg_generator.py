#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG生成器测试脚本
"""

import os
import sys
from simple_svg_generator import SimpleSVGGenerator

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试SVG生成器...")
    
    # 检查环境变量
    api_key = os.getenv('ALIYUN_API_KEY')
    if not api_key:
        print("❌ 未设置ALIYUN_API_KEY环境变量")
        print("💡 请运行: export ALIYUN_API_KEY='your-api-key'")
        return False
    
    print("✅ API密钥已设置")
    
    # 检查测试文件
    test_files = ['chapter_01_1.2.1.3.1.1 自注意力机制的信息聚合原理.txt']
    missing_files = [f for f in test_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少测试文件: {missing_files}")
        return False
    
    print("✅ 测试文件存在")
    
    # 初始化生成器
    try:
        generator = SimpleSVGGenerator()
        print("✅ 生成器初始化成功")
    except Exception as e:
        print(f"❌ 生成器初始化失败: {e}")
        return False
    
    # 测试文件解析
    try:
        chapter_num, title = generator.parse_filename(test_files[0])
        print(f"✅ 文件解析成功: 章节{chapter_num} - {title}")
    except Exception as e:
        print(f"❌ 文件解析失败: {e}")
        return False
    
    # 测试SVG模板生成
    try:
        test_content = "这是测试内容的预览..."
        svg_content = generator.create_professional_svg_template(title, test_content)
        
        if '<svg' in svg_content and '1920' in svg_content:
            print("✅ SVG模板生成成功")
        else:
            print("❌ SVG模板生成失败")
            return False
    except Exception as e:
        print(f"❌ SVG模板生成异常: {e}")
        return False
    
    print("🎉 所有基础测试通过!")
    return True

def test_file_operations():
    """测试文件操作功能"""
    print("\n📂 测试文件操作...")
    
    # 测试目录创建
    test_dir = "test_output"
    try:
        os.makedirs(test_dir, exist_ok=True)
        print("✅ 输出目录创建成功")
    except Exception as e:
        print(f"❌ 目录创建失败: {e}")
        return False
    
    # 测试文件写入
    test_file = os.path.join(test_dir, "test.svg")
    test_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
    <rect width="1920" height="1080" fill="#f0f0f0"/>
    <text x="100" y="100" font-family="Arial">Test</text>
</svg>'''
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        print("✅ SVG文件写入成功")
    except Exception as e:
        print(f"❌ 文件写入失败: {e}")
        return False
    
    # 清理测试文件
    try:
        os.remove(test_file)
        os.rmdir(test_dir)
        print("✅ 测试文件清理成功")
    except Exception as e:
        print(f"⚠️  文件清理警告: {e}")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("     SVG生成器功能测试")
    print("=" * 50)
    
    success = True
    
    # 运行各项测试
    if not test_basic_functionality():
        success = False
    
    if not test_file_operations():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！可以开始正式生成。")
        print("\n💡 使用方法:")
        print("   ./run_ppt_generation.sh")
        print("   或")
        print("   python3 simple_svg_generator.py")
    else:
        print("❌ 部分测试失败，请检查环境配置。")
    print("=" * 50)