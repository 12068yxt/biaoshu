#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整使用示例脚本
演示五级和六级标题处理的完整使用流程
"""

import json
import asyncio
from sample.concurrent_expand import ConcurrentDocumentExpander

async def process_with_fifth_level_titles():
    """使用五级标题处理文档"""
    print("=" * 60)
    print("使用五级标题处理文档示例")
    print("=" * 60)
    
    # 修改配置为五级标题
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    config["title_settings"]["title_level"] = 5
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✓ 配置已切换到五级标题处理模式")
    
    # 创建扩充器并处理
    expander = ConcurrentDocumentExpander()
    await expander.process_document()

async def process_with_sixth_level_titles():
    """使用六级标题处理文档"""
    print("\n" + "=" * 60)
    print("使用六级标题处理文档示例")
    print("=" * 60)
    
    # 修改配置为六级标题
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    config["title_settings"]["title_level"] = 6
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✓ 配置已切换到六级标题处理模式")
    
    # 创建扩充器并处理
    expander = ConcurrentDocumentExpander()
    await expander.process_document()

def show_comparison():
    """显示两种处理模式的对比"""
    print("\n" + "=" * 60)
    print("处理模式对比")
    print("=" * 60)
    
    from sample.concurrent_expand import ConcurrentDocumentExpander
    expander = ConcurrentDocumentExpander()
    
    with open("工作原理.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    fifth_titles = expander.extract_all_fifth_level_titles(content)
    sixth_titles = expander.extract_all_sixth_level_titles(content)
    
    print("标题数量对比:")
    print(f"  五级标题: {len(fifth_titles):3d} 个")
    print(f"  六级标题: {len(sixth_titles):3d} 个")
    print(f"  数量差异: {len(sixth_titles) - len(fifth_titles):3d} 个")
    
    print("\n处理特点对比:")
    print("  五级标题处理:")
    print("    • 处理章节较少，内容更宏观")
    print("    • 适合概要性内容扩充")
    print("    • 生成时间相对较短")
    
    print("\n  六级标题处理:")
    print("    • 处理章节较多，内容更详细")
    print("    • 适合深度技术细节扩充")
    print("    • 生成时间相对较长")

async def main():
    """主函数 - 演示完整使用流程"""
    print("大模型文档扩充工具 - 完整使用示例")
    print("注意: 此演示需要有效的 ALIYUN_API_KEY 环境变量")
    
    # 显示对比信息
    show_comparison()
    
    # 检查API密钥
    import os
    if not os.getenv("ALIYUN_API_KEY"):
        print("\n⚠️  警告: 未设置 ALIYUN_API_KEY 环境变量")
        print("请先设置环境变量后再运行完整处理:")
        print("  export ALIYUN_API_KEY='your-api-key-here'")
        return
    
    # 询问用户选择
    print("\n请选择处理模式:")
    print("1. 五级标题处理 (较少章节，较快速度)")
    print("2. 六级标题处理 (较多章节，较详细内容)")
    print("3. 退出")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            await process_with_fifth_level_titles()
        elif choice == "2":
            await process_with_sixth_level_titles()
        elif choice == "3":
            print("退出演示")
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n\n用户中断操作")

if __name__ == "__main__":
    asyncio.run(main())