#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能跳过版文档扩充脚本
自动检测已生成内容并跳过，避免重复处理
"""

import asyncio
import aiohttp
import json
import os
import re
import time
from typing import List, Dict, Set
from asyncio import Semaphore
import random

class SmartSkipExpander:
    """智能跳过文档扩充器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.title_level = self.config.get("title_settings", {}).get("title_level", 6)
        # 降低并发确保稳定性
        self.semaphore = Semaphore(1)
        
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "api_settings": {"temperature": 0.7, "max_tokens": 3000, "timeout": 180},
                "title_settings": {"title_level": 6}
            }
    
    def extract_titles(self, content: str) -> List[str]:
        """提取六级标题"""
        titles = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('### ') and not line.startswith('####'):
                pattern = r'^###\s+(\d+(?:\.\d+)*)\.\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = re.sub(r'\(\d+页\)$', '', match.group(2)).strip()
                    titles.append(f"{number} {title_text}")
        return titles
    
    def get_existing_chapters(self) -> Set[str]:
        """获取已存在的章节文件"""
        existing_titles = set()
        
        # 查找现有的章节文件
        for filename in os.listdir('.'):
            if filename.startswith('chapter_') and filename.endswith('.md'):
                # 提取标题信息
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('章节标题:'):
                            title = first_line.replace('章节标题:', '').strip()
                            existing_titles.add(title)
                        elif first_line.startswith('章节:'):
                            title = first_line.replace('章节:', '').strip()
                            existing_titles.add(title)
                except Exception:
                    continue
        
        print(f"🔍 检测到 {len(existing_titles)} 个已存在的章节")
        return existing_titles
    
    def get_completed_titles_from_main_file(self, main_file: str) -> Set[str]:
        """从主输出文件中提取已完成的标题"""
        completed_titles = set()
        try:
            if os.path.exists(main_file):
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找章节标题模式
                title_pattern = r'### (\d+(?:\.\d+)*)\s+(.+?)(?=\n#{2,}|$)'
                matches = re.findall(title_pattern, content, re.DOTALL)
                
                for number, title_text in matches:
                    # 清理标题文本
                    clean_title = re.sub(r'\(\d+页\)$', '', title_text).strip()
                    full_title = f"{number} {clean_title}"
                    completed_titles.add(full_title)
                
                print(f"📄 从主文件检测到 {len(completed_titles)} 个已完成章节")
        except Exception as e:
            print(f"⚠ 读取主文件时出错: {e}")
        
        return completed_titles
    
    async def call_api_safe(self, session: aiohttp.ClientSession, prompt: str, title: str) -> tuple:
        """安全的API调用"""
        max_retries = 5
        base_delay = 6
        
        for attempt in range(max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'qwen-plus',
                    'input': {'prompt': prompt},
                    'parameters': {
                        'temperature': 0.7,
                        'max_tokens': 3000
                    }
                }
                
                url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                timeout = aiohttp.ClientTimeout(total=180, connect=30, sock_read=90)
                
                if attempt > 0:
                    delay = base_delay * (1.5 ** attempt) + random.uniform(0, 3)
                    print(f"    ⏳ 第{attempt}次重试，等待{delay:.1f}秒...")
                    await asyncio.sleep(delay)
                
                async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('output', {}).get('text', '')
                        if len(content) >= 800:
                            return True, content, attempt + 1
                    elif response.status == 429:
                        print(f"    ⚠ 速率限制，延长等待...")
                        await asyncio.sleep(30 + random.uniform(5, 10))
                    else:
                        print(f"    ⚠ HTTP {response.status}")
                        
            except Exception as e:
                print(f"    ⚠ 异常: {str(e)[:50]}")
                await asyncio.sleep(10 + random.uniform(2, 5))
        
        return False, "", max_retries
    
    def create_prompt(self, title: str) -> str:
        """创建提示词"""
        return f"""请详细解释以下技术主题：

{title}

要求：
1. 用连续段落写作
2. 保持专业技术文档风格  
3. 全中文，内容详实
4. 至少1500字

详细阐述："""
    
    async def process_remaining_titles(self, session: aiohttp.ClientSession, 
                                     remaining_titles: List[str], 
                                     output_file: str) -> Dict:
        """处理剩余需要生成的标题"""
        print(f"\n🚀 开始处理 {len(remaining_titles)} 个待生成章节")
        results = {"successful": 0, "failed": 0, "processed": []}
        
        for i, title in enumerate(remaining_titles, 1):
            print(f"[{i}/{len(remaining_titles)}] 处理: {title}")
            
            prompt = self.create_prompt(title)
            success, content, attempts = await self.call_api_safe(session, prompt, title)
            
            if success:
                # 保存到主文件
                separator = "\n\n" + "="*30 + "\n"
                header = f"### {title}\n\n"
                
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(separator)
                    f.write(header)
                    f.write(content)
                    f.write("\n")
                
                # 保存独立文件
                self.save_individual_file(title, content)
                
                print(f"    ✅ 成功 ({len(content)}字符, {attempts}次尝试)")
                results["successful"] += 1
            else:
                print(f"    ❌ 失败 ({attempts}次尝试)")
                results["failed"] += 1
            
            results["processed"].append({
                "title": title,
                "success": success,
                "attempts": attempts
            })
            
            # 章节间间隔
            if i < len(remaining_titles):
                await asyncio.sleep(random.uniform(2, 4))
        
        return results
    
    def save_individual_file(self, title: str, content: str):
        """保存独立文件"""
        match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
        if match:
            number, title_name = match.groups()
            clean_name = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
            clean_name = re.sub(r'_+', '_', clean_name).strip('_')
            filename = f"chapter_{number}._{clean_name}_smart.md"
        else:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            filename = f"chapter_{clean_title}_smart.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"章节: {title}\n")
            f.write("="*30 + "\n\n")
            f.write(content)
    
    async def smart_process(self):
        """智能处理主函数"""
        # 读取文档
        document_settings = self.config.get("document_settings", {})
        source_file = document_settings.get("source_file", "模型架构.md")
        file_name, ext = os.path.splitext(source_file)
        output_file = f"{file_name}_smart{ext}"
        
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✅ 读取源文档: {source_file}")
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return
        
        # 提取所有标题
        all_titles = self.extract_titles(content)
        print(f"📚 发现 {len(all_titles)} 个六级标题")
        
        if not all_titles:
            print("❌ 未找到标题")
            return
        
        # 检测已存在的内容
        existing_chapters = self.get_existing_chapters()
        completed_from_main = self.get_completed_titles_from_main_file(output_file)
        
        # 合并已存在的标题
        already_done = existing_chapters.union(completed_from_main)
        
        # 筛选出需要处理的标题
        remaining_titles = [title for title in all_titles if title not in already_done]
        
        print(f"\n📊 处理统计:")
        print(f"  总章节数: {len(all_titles)}")
        print(f"  已完成: {len(already_done)}")
        print(f"  待处理: {len(remaining_titles)}")
        
        if not remaining_titles:
            print("🎉 所有章节均已生成，无需进一步处理!")
            return
        
        print(f"🎯 将处理以下章节:")
        for i, title in enumerate(remaining_titles, 1):
            print(f"  {i}. {title}")
        
        # 确认处理
        confirm = input(f"\n确认处理这 {len(remaining_titles)} 个章节? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 操作已取消")
            return
        
        # HTTP会话配置
        timeout = aiohttp.ClientTimeout(total=240, connect=30, sock_read=120)
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1, keepalive_timeout=30)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            results = await self.process_remaining_titles(session, remaining_titles, output_file)
        
        # 统计总结
        total_time = time.time() - start_time
        
        print("\n" + "="*50)
        print("📊 智能处理完成")
        print(f"📄 输出文件: {output_file}")
        print(f"📈 处理章节数: {len(remaining_titles)}")
        print(f"✅ 成功: {results['successful']}")
        print(f"❌ 失败: {results['failed']}")
        print(f"🎯 成功率: {results['successful']/len(remaining_titles)*100:.1f}%")
        print(f"⏱️ 总耗时: {total_time/60:.1f}分钟")

async def main():
    """主函数"""
    print("🔍 智能跳过版文档扩充工具")
    print("💡 自动检测已生成内容并跳过重复处理")
    print("="*40)
    
    expander = SmartSkipExpander()
    await expander.smart_process()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠ 操作中断")
    except Exception as e:
        print(f"\n💥 错误: {e}")
        import traceback
        traceback.print_exc()