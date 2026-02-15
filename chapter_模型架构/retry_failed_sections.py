#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失败章节重试工具
专门用于重新处理之前运行中失败的章节
"""

import asyncio
import aiohttp
import json
import os
import re
import time
from typing import List, Dict
from concurrent_expand import ConcurrentDocumentExpander

class FailedSectionRetrier:
    def __init__(self, config_file: str = "config.json"):
        self.expander = ConcurrentDocumentExpander(config_file)
        self.failed_sections = []
    
    def extract_failed_sections_from_log(self, log_file: str = "expansion_detailed_log.txt") -> List[str]:
        """从日志文件中提取失败的章节"""
        failed_sections = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找失败的章节标记
            failed_pattern = r'✗\s+(.*?)\s+处理失败'
            matches = re.findall(failed_pattern, content)
            failed_sections.extend(matches)
            
            # 也可以查找重试失败的章节
            retry_failed_pattern = r'✗\s+(.*?)\s+第\d+次尝试失败'
            retry_matches = re.findall(retry_failed_pattern, content)
            failed_sections.extend(retry_matches)
            
            # 去重
            return list(set(failed_sections))
            
        except FileNotFoundError:
            print(f"日志文件 {log_file} 未找到")
            return []
        except Exception as e:
            print(f"读取日志文件出错: {str(e)}")
            return []
    
    def extract_failed_sections_from_output(self, output_file: str) -> List[str]:
        """从输出文件中提取未完成的章节"""
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找只有标题但没有内容的部分
            # 这种情况比较复杂，需要根据具体的输出格式来判断
            return []
            
        except FileNotFoundError:
            print(f"输出文件 {output_file} 未找到")
            return []
        except Exception as e:
            print(f"读取输出文件出错: {str(e)}")
            return []
    
    async def retry_single_section(self, session: aiohttp.ClientSession, title: str, output_file: str) -> Dict:
        """重试单个章节"""
        print(f"🔄 重试章节: {title}")
        
        prompt = self.expander.create_prompt(title)
        max_retries = 5  # 给失败章节更多重试机会
        
        for attempt in range(max_retries):
            try:
                content = await self.expander.call_aliyun_api(session, prompt)
                
                if content and len(content) >= 1000:
                    print(f"✅ {title} 重试成功 ({len(content)} 字符)")
                    
                    # 追加到输出文件
                    self.expander.append_to_markdown_file(title, content, output_file)
                    
                    return {
                        "title": title,
                        "content": content,
                        "status": "success",
                        "characters": len(content),
                        "attempts": attempt + 1
                    }
                else:
                    print(f"❌ {title} 重试第{attempt+1}次失败 - 内容不足")
                    await asyncio.sleep(10 * (attempt + 1))  # 递增延迟
                    
            except Exception as e:
                print(f"❌ {title} 重试第{attempt+1}次异常: {str(e)}")
                await asyncio.sleep(15 * (attempt + 1))
        
        print(f"💥 {title} 重试最终失败")
        return {
            "title": title,
            "content": "",
            "status": "failed",
            "characters": 0,
            "attempts": max_retries
        }
    
    async def retry_failed_sections(self, failed_sections: List[str], output_file: str = None):
        """重试所有失败的章节"""
        if not failed_sections:
            print("🎉 没有发现失败的章节！")
            return
        
        print(f"🔧 发现 {len(failed_sections)} 个失败章节，开始重试...")
        
        if not output_file:
            # 自动生成输出文件名
            document_settings = self.expander.config.get("document_settings", {})
            source_file = document_settings.get("source_file", "工作原理.md")
            file_name, file_ext = os.path.splitext(source_file)
            output_file = f"{file_name}_expanded{file_ext}"
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=180, connect=30, sock_read=90)
        connector = aiohttp.TCPConnector(limit=2, limit_per_host=2)  # 减少并发以提高成功率
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # 逐个处理失败章节（降低并发）
            results = []
            for i, title in enumerate(failed_sections, 1):
                print(f"\n[{i}/{len(failed_sections)}] 处理失败章节...")
                result = await self.retry_single_section(session, title, output_file)
                results.append(result)
                
                # 每处理完一个章节后短暂休息
                if i < len(failed_sections):
                    await asyncio.sleep(5)
        
        # 统计结果
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful
        total_chars = sum(r.get("characters", 0) for r in results)
        
        print("\n" + "="*50)
        print("🔧 重试完成统计:")
        print(f"📋 总失败章节: {len(failed_sections)}")
        print(f"✅ 重试成功: {successful}")
        print(f"❌ 仍然失败: {failed}")
        print(f"🎯 重试成功率: {successful/len(failed_sections)*100:.1f}%" if failed_sections else "0%")
        if successful > 0:
            print(f"🔤 新增字符数: {total_chars:,}")

def main():
    """主函数"""
    print("🔧 失败章节重试工具")
    print("="*30)
    
    # 询问用户来源
    print("请选择失败章节来源:")
    print("1. 从日志文件提取")
    print("2. 手动输入章节标题")
    print("3. 从输出文件分析（开发中）")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    retrier = FailedSectionRetrier()
    
    failed_sections = []
    
    if choice == "1":
        log_file = input("请输入日志文件名 (默认: expansion_detailed_log.txt): ").strip()
        log_file = log_file or "expansion_detailed_log.txt"
        failed_sections = retrier.extract_failed_sections_from_log(log_file)
        print(f"🔍 从日志中找到 {len(failed_sections)} 个失败章节")
        
    elif choice == "2":
        print("请输入失败的章节标题（每行一个，空行结束）:")
        while True:
            title = input().strip()
            if not title:
                break
            failed_sections.append(title)
        print(f"📝 输入了 {len(failed_sections)} 个章节")
        
    elif choice == "3":
        output_file = input("请输入输出文件名: ").strip()
        if output_file:
            failed_sections = retrier.extract_failed_sections_from_output(output_file)
            print(f"🔍 从输出文件中找到 {len(failed_sections)} 个未完成章节")
        else:
            print("❌ 未指定输出文件")
            return
    else:
        print("❌ 无效选择")
        return
    
    if not failed_sections:
        print("🎉 没有发现需要重试的章节")
        return
    
    # 显示要重试的章节
    print("\n📋 将要重试的章节:")
    for i, title in enumerate(failed_sections, 1):
        print(f"  {i}. {title}")
    
    confirm = input("\n确认开始重试? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    # 执行重试
    asyncio.run(retrier.retry_failed_sections(failed_sections))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ 操作被用户中断")
    except Exception as e:
        print(f"\n💥 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()