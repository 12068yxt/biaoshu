#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可配置文档文件路径功能
"""

import json
import os
from sample.concurrent_expand import ConcurrentDocumentExpander

def test_document_configuration():
    """测试文档配置功能"""
    print("=" * 60)
    print("文档文件路径配置测试")
    print("=" * 60)
    
    # 测试默认配置
    print("\n1. 测试默认配置:")
    expander = ConcurrentDocumentExpander()
    document_settings = expander.config.get("document_settings", {})
    source_file = document_settings.get('source_file', '未设置')
    
    # 演示自动输出文件名生成
    if source_file != '未设置':
        file_name, file_ext = os.path.splitext(source_file)
        auto_output_file = f"{file_name}_expanded{file_ext}"
    else:
        auto_output_file = '未设置'
    
    print(f"  源文档: {source_file}")
    print(f"  自动生成的输出文件: {auto_output_file}")
    
    # 测试切换到text.md
    print("\n2. 切换到text.md配置:")
    
    # 备份当前配置
    with open("config.json", "r", encoding="utf-8") as f:
        original_config = json.load(f)
    
    # 修改配置为text.md（不设置output_file以测试自动命名）
    new_config = original_config.copy()
    new_config["document_settings"] = {
        "source_file": "text.md",
        "supported_extensions": [".md", ".txt"]
    }
    
    # 保存新配置
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=2)
    
    print("✓ 配置已更新为text.md")
    
    # 测试新配置的自动命名
    expander_new = ConcurrentDocumentExpander()
    document_settings_new = expander_new.config.get("document_settings", {})
    new_source_file = document_settings_new.get('source_file')
    new_file_name, new_file_ext = os.path.splitext(new_source_file)
    new_auto_output = f"{new_file_name}_expanded{new_file_ext}"
    
    print(f"  新源文档: {new_source_file}")
    print(f"  自动生成的输出文件: {new_auto_output}")
    
    # 恢复原始配置
    print("\n3. 恢复原始配置:")
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(original_config, f, ensure_ascii=False, indent=2)
    print("✓ 配置已恢复")
    
    # 验证配置恢复
    expander_restored = ConcurrentDocumentExpander()
    document_settings_restored = expander_restored.config.get("document_settings", {})
    print(f"  恢复后源文档: {document_settings_restored.get('source_file')}")

def show_available_documents():
    """显示可用的文档文件"""
    print("\n" + "=" * 60)
    print("可用文档文件")
    print("=" * 60)
    
    import glob
    
    # 查找markdown和txt文件
    md_files = glob.glob("*.md")
    txt_files = glob.glob("*.txt")
    
    print("Markdown文件:")
    for file in md_files:
        size = os.path.getsize(file)
        file_name, file_ext = os.path.splitext(file)
        auto_output = f"{file_name}_expanded{file_ext}"
        print(f"  - {file} ({size:,} 字节) → 自动输出: {auto_output}")
    
    print("\n文本文件:")
    for file in txt_files:
        size = os.path.getsize(file)
        file_name, file_ext = os.path.splitext(file)
        auto_output = f"{file_name}_expanded{file_ext}"
        print(f"  - {file} ({size:,} 字节) → 自动输出: {auto_output}")

def demonstrate_usage():
    """演示使用方法"""
    print("\n" + "=" * 60)
    print("使用方法演示")
    print("=" * 60)
    
    print("在 config.json 中只需配置源文档:")
    print("""{
  "document_settings": {
    "source_file": "text.md",
    "supported_extensions": [".md", ".txt"]
  }
}""")
    
    print("\n输出文件将自动生成为: text_expanded.md")
    print("\n然后运行:")
    print("uv run python concurrent_expand.py")

if __name__ == "__main__":
    test_document_configuration()
    show_available_documents()
    demonstrate_usage()
    print("\n配置测试完成!")