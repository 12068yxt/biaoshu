#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渐进式文档扩充脚本
采用小批量验证→逐步扩大的方式处理文档
"""

import asyncio
import aiohttp
import json
import os
import re
import time
from typing import List, Dict
from asyncio import Semaphore
import random

class ProgressiveExpander:
    """渐进式文档扩充器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.title_level = self.config.get("title_settings", {}).get("title_level", 6)
        
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "api_settings": {"temperature": 0.7, "max_tokens": 3000, "timeout": 180},
                "title_settings": {"title_level": 6},
                "processing_settings": {"batch_size": 3, "retry_attempts": 6}
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
    
    async def call_api_safely(self, session: aiohttp.ClientSession, prompt: str, title: str) -> tuple:
        """安全的API调用"""
        max_retries = 6
        base_delay = 8
        
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
                    delay = base_delay * (1.5 ** attempt) + random.uniform(0, 5)
                    print(f"    ⏳ 第{attempt}次重试，等待{delay:.1f}秒...")
                    await asyncio.sleep(delay)
                
                async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('output', {}).get('text', '')
                        if len(content) >= 800:
                            return True, content, attempt + 1
                        else:
                            print(f"    ⚠ 内容长度不足 ({len(content)}字符)")
                    elif response.status == 429:
                        print(f"    ⚠ 速率限制，等待更长时间...")
                        await asyncio.sleep(45 + random.uniform(5, 15))
                    else:
                        print(f"    ⚠ HTTP {response.status} 错误")
                        
            except Exception as e:
                print(f"    ⚠ 异常: {str(e)[:50]}")
                if "timeout" in str(e).lower():
                    await asyncio.sleep(20 + random.uniform(5, 10))
                else:
                    await asyncio.sleep(15 + random.uniform(3, 8))
        
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
    
    async def process_batch(self, session: aiohttp.ClientSession, titles: List[str], 
                          batch_num: int, total_batches: int, output_file: str) -> Dict:
        """处理一批章节"""
        print(f"\n📦 批次 {batch_num}/{total_batches} 开始处理 ({len(titles)}个章节)")
        batch_results = {"successful": 0, "failed": 0, "details": []}
        
        for i, title in enumerate(titles, 1):
            print(f"  [{i}/{len(titles)}] 处理: {title}")
            
            prompt = self.create_prompt(title)
            success, content, attempts = await self.call_api_safely(session, prompt, title)
            
            if success:
                # 保存内容
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
                batch_results["successful"] += 1
            else:
                print(f"    ❌ 失败 ({attempts}次尝试)")
                batch_results["failed"] += 1
            
            batch_results["details"].append({
                "title": title,
                "success": success,
                "attempts": attempts
            })
            
            # 批次内间隔
            if i < len(titles):
                await asyncio.sleep(random.uniform(3, 6))
        
        return batch_results
    
    def save_individual_file(self, title: str, content: str):
        """保存独立文件"""
        match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
        if match:
            number, title_name = match.groups()
            clean_name = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
            clean_name = re.sub(r'_+', '_', clean_name).strip('_')
            filename = f"chapter_{number}._{clean_name}_progressive.md"
        else:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            filename = f"chapter_{clean_title}_progressive.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"章节: {title}\n")
            f.write("="*30 + "\n\n")
            f.write(content)
    
    async def progressive_process(self):
        """渐进式处理主函数"""
        # 读取文档
        document_settings = self.config.get("document_settings", {})
        source_file = document_settings.get("source_file", "模型架构.md")
        file_name, ext = os.path.splitext(source_file)
        output_file = f"{file_name}_progressive{ext}"
        
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✅ 读取源文档: {source_file}")
        except Exception as e:
            print(f"❌ 读取失败: {e}")
            return
        
        # 提取标题
        titles = self.extract_titles(content)
        print(f"📚 发现 {len(titles)} 个六级标题")
        
        if not titles:
            print("❌ 未找到标题")
            return
        
        # 分批处理
        batch_size = 2  # 小批次
        batches = [titles[i:i + batch_size] for i in range(0, len(titles), batch_size)]
        
        print(f"📋 计划分为 {len(batches)} 个批次，每批 {batch_size} 个章节")
        
        # HTTP会话配置
        timeout = aiohttp.ClientTimeout(total=240, connect=30, sock_read=120)
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1, keepalive_timeout=30)
        
        total_start_time = time.time()
        all_results = []
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            for batch_num, batch_titles in enumerate(batches, 1):
                batch_result = await self.process_batch(
                    session, batch_titles, batch_num, len(batches), output_file
                )
                all_results.append(batch_result)
                
                # 批次间休息
                if batch_num < len(batches):
                    rest_time = random.uniform(10, 20)
                    print(f"💤 批次间休息 {rest_time:.1f} 秒...")
                    await asyncio.sleep(rest_time)
        
        # 统计总结
        total_time = time.time() - total_start_time
        total_successful = sum(r["successful"] for r in all_results)
        total_failed = sum(r["failed"] for r in all_results)
        
        print("\n" + "="*50)
        print("📊 渐进式处理完成")
        print(f"📄 输出文件: {output_file}")
        print(f"📈 总章节数: {len(titles)}")
        print(f"✅ 成功: {total_successful}")
        print(f"❌ 失败: {total_failed}")
        print(f"🎯 成功率: {total_successful/len(titles)*100:.1f}%")
        print(f"⏱️ 总耗时: {total_time/60:.1f}分钟")

async def main():
    """主函数"""
    print("🐢 渐进式文档扩充工具")
    print("💡 小批量验证→逐步扩大策略")
    print("="*40)
    
    expander = ProgressiveExpander()
    await expander.progressive_process()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠ 操作中断")
    except Exception as e:
        print(f"\n💥 错误: {e}")
        import traceback
        traceback.print_exc()