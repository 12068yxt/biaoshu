#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批处理工作原理文档扩充
"""

import asyncio
import json
import os
import time
from typing import List, Dict
from expand import AdvancedContentExpander

def load_chapters():
    """加载所有章节标题"""
    with open("sixth_level_titles.txt", "r", encoding="utf-8") as f:
        chapters = [line.strip() for line in f.readlines()]
    return chapters

def split_into_batches(chapters: List[str], batch_size: int = 5) -> List[List[str]]:
    """将章节分成批次"""
    batches = []
    for i in range(0, len(chapters), batch_size):
        batch = chapters[i:i + batch_size]
        batches.append(batch)
    return batches

async def process_batch(expander: AdvancedContentExpander, batch: List[str], batch_num: int):
    """处理单个批次"""
    print(f"\n开始处理第 {batch_num} 批次 ({len(batch)} 个章节)")
    print("-" * 40)
    
    try:
        # 为每个批次创建新的expander实例
        batch_expander = AdvancedContentExpander()
        results = await batch_expander.expand_sections_parallel(batch)
        
        if results:
            print(f"✓ 第 {batch_num} 批次完成，成功处理 {len(results)} 个章节")
            # 保存批次结果
            batch_file = f"batch_{batch_num}_results.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {batch_file}")
            return results
        else:
            print(f"✗ 第 {batch_num} 批次失败")
            return {}
            
    except Exception as e:
        print(f"✗ 第 {batch_num} 批次出现错误: {str(e)}")
        return {}

async def main():
    """主函数"""
    print("开始分批处理工作原理文档扩充")
    print("=" * 50)
    
    # 加载所有章节
    chapters = load_chapters()
    print(f"总共 {len(chapters)} 个章节")
    
    # 分成批次（每批5个章节）
    batches = split_into_batches(chapters, batch_size=5)
    print(f"分成 {len(batches)} 个批次处理")
    
    # 处理每个批次
    all_results = {}
    
    for i, batch in enumerate(batches, 1):
        print(f"\n处理进度: {i}/{len(batches)}")
        
        batch_results = await process_batch(None, batch, i)
        all_results.update(batch_results)
        
        # 每批之间等待一段时间
        if i < len(batches):
            wait_time = 30  # 等待30秒
            print(f"等待 {wait_time} 秒后处理下一批...")
            time.sleep(wait_time)
    
    # 生成最终报告
    print("\n" + "=" * 50)
    print("处理完成汇总")
    print("=" * 50)
    print(f"总章节数: {len(chapters)}")
    print(f"成功处理: {len(all_results)}")
    print(f"成功率: {len(all_results)/len(chapters)*100:.1f}%")
    
    if all_results:
        total_chars = sum(len(content) for content in all_results.values())
        print(f"总字符数: {total_chars:,}")
        print(f"平均每个章节: {total_chars/len(all_results):,.0f} 字符")
        
        # 保存完整结果
        with open("complete_results.json", 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("完整结果已保存到: complete_results.json")

if __name__ == "__main__":
    asyncio.run(main())