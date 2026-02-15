#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顺序处理工作原理文档扩充（单线程版）
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import List, Dict, Optional

async def call_aliyun_api(api_key: str, prompt: str) -> Optional[str]:
    """调用阿里云API生成内容"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'qwen-plus',
        'input': {
            'prompt': prompt
        },
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 3500  # 稍微减少token数避免超时
        }
    }
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    try:
        timeout = aiohttp.ClientTimeout(total=120)  # 增加超时时间到120秒
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('output', {}).get('text', '')
                else:
                    error_text = await response.text()
                    print(f"API调用失败: {response.status}, 错误: {error_text}")
                    return None
    except Exception as e:
        print(f"API调用异常: {str(e)}")
        return None

def create_prompt(title: str) -> str:
    """为章节标题创建提示词"""
    return f"""

作为一名资深的大模型技术专家和技术标书撰写顾问，请详细扩充以下技术内容：
主题：{title}

写作要求：
1. 采用连续自然段落形式，避免数字编号和条列式结构
2. 使用专业、严谨、逻辑严密的技术标书语言风格
3. 保持正式规范的文体，注重基础概念解释与技术内涵延展
4. 全中文写作，详细介绍技术原理、实现细节等，避免使用数学符号，数学公式
5. 内容详实深入，每个部分3000字左右
6. 风格类似于非常啰嗦的老师，即详尽、重复强调、层层展开，确保信息密度高且表述完整
7. 模仿技术标书的专业写作风格，注重术语解释、概念延展与技术深度


请开始详细阐述："""

def save_individual_result(title: str, content: str, index: int):
    """保存单个章节的结果"""
    # 创建单独的文件保存每个章节
    filename = f"chapter_{index:02d}_{title.replace('/', '_').replace(':', '_')[:50]}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"章节标题: {title}\n")
        f.write(f"章节编号: {index}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)
    print(f"✓ 内容已保存到: {filename}")

def append_to_markdown(title: str, content: str):
    """将内容追加到工作原理.md文件"""
    with open("工作原理.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n### {title}\n\n")
        f.write(content)
        f.write("\n\n---\n")
    print(f"✓ 内容已追加到 工作原理.md")

def save_progress(results: Dict[str, str]):
    """保存当前进度"""
    # 保存完整的进度文件
    with open("current_progress.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存简洁的进度报告
    with open("progress_report.txt", 'w', encoding='utf-8') as f:
        f.write(f"处理进度报告\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"已完成章节: {len(results)}\n")
        f.write(f"总字符数: {sum(len(content) for content in results.values()):,}\n")
        f.write("=" * 30 + "\n")
        for i, (title, content) in enumerate(results.items(), 1):
            f.write(f"{i}. {title} ({len(content)} 字符)\n")

async def process_single_chapter(api_key: str, title: str, index: int, total: int, results: Dict[str, str]) -> bool:
    """处理单个章节并立即保存"""
    print(f"[{index}/{total}] 正在处理: {title}")
    
    prompt = create_prompt(title)
    
    # 重试机制
    for attempt in range(3):
        try:
            content = await call_aliyun_api(api_key, prompt)
            if content and len(content) > 1000:
                print(f"✓ 成功生成 {len(content)} 字符")
                
                # 立即保存单个章节
                save_individual_result(title, content, index)
                
                # 追加到工作原理.md
                append_to_markdown(title, content)
                
                # 更新结果字典
                results[title] = content
                
                # 立即保存进度
                save_progress(results)
                
                return True
            else:
                print(f"✗ 内容不足，第{attempt+1}次重试")
                await asyncio.sleep(10 * (attempt + 1))  # 递增等待时间
        except Exception as e:
            print(f"✗ 第{attempt+1}次尝试失败: {str(e)}")
            await asyncio.sleep(15 * (attempt + 1))
    
    print(f"✗ {title} 处理失败")
    return False

async def main():
    """主函数"""
    api_key = "sk-19278db0ad4b436d9bf381e0c04c56dc"
    
    # 读取章节标题
    with open("sixth_level_titles.txt", "r", encoding="utf-8") as f:
        chapters = [line.strip() for line in f.readlines()]
    
    print(f"开始顺序处理 {len(chapters)} 个章节")
    print("=" * 50)
    
    results = {}
    successful_count = 0
    
    # 顺序处理每个章节
    for i, chapter in enumerate(chapters, 1):
        success = await process_single_chapter(api_key, chapter, i, len(chapters), results)
        
        if success:
            successful_count += 1
        
        # 已移除章节间的等待时间
    
    # 生成最终报告
    print("\n" + "=" * 50)
    print("处理完成!")
    print("=" * 50)
    print(f"总章节数: {len(chapters)}")
    print(f"成功处理: {successful_count}")
    print(f"成功率: {successful_count/len(chapters)*100:.1f}%")
    
    if results:
        total_chars = sum(len(content) for content in results.values())
        print(f"总字符数: {total_chars:,}")
        print(f"平均每个章节: {total_chars/len(results):,.0f} 字符")
        
        # 保存最终完整结果
        with open("sequential_results_final.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("最终结果已保存到: sequential_results_final.json")

if __name__ == "__main__":
    asyncio.run(main())