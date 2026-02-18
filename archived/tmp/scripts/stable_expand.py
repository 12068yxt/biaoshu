#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定版文档扩充脚本
专门针对"部分成功部分失败"问题设计
采用更加保守的策略确保最大成功率
"""

import asyncio
import aiohttp
import json
import os
import re
import time
from typing import List, Dict, Optional
from asyncio import Semaphore
import random
from datetime import datetime

class StableDocumentExpander:
    """稳定版文档扩充器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        # 降低并发数以提高稳定性
        self.semaphore = Semaphore(1)  # 只允许1个并发请求
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.title_level = self.config.get("title_settings", {}).get("title_level", 6)
        self.processing_settings = self.config.get("processing_settings", {})
        self.max_retries = self.processing_settings.get("retry_attempts", 8)  # 增加重试次数
        self.min_content_length = self.processing_settings.get("min_content_length", 800)  # 降低最小长度要求
        
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 未找到，使用默认配置")
            return {
                "api_settings": {
                    "temperature": 0.7,
                    "max_tokens": 3500,
                    "timeout": 240  # 增加超时时间
                },
                "title_settings": {
                    "title_level": 6
                },
                "processing_settings": {
                    "retry_attempts": 8,
                    "min_content_length": 800
                }
            }
    
    def extract_all_titles(self, content: str, level: int = 6) -> List[str]:
        """提取指定级别的所有标题"""
        if level == 5:
            return self.extract_all_fifth_level_titles(content)
        elif level == 6:
            return self.extract_all_sixth_level_titles(content)
        elif level == 7:
            return self.extract_all_seventh_level_titles(content)
        else:
            raise ValueError(f"不支持的标题级别: {level}，支持5级、6级或7级标题")
    
    def extract_all_sixth_level_titles(self, content: str) -> List[str]:
        """提取所有六级标题"""
        titles = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 处理标准的六级标题 (### 1.2.2.11.1. 标题)
            if line.startswith('### '):
                pattern = r'^###\s+(\d+(?:\.\d+)*)\.\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = match.group(2)
                    # 移除可能的页数信息
                    title_text = re.sub(r'\(\d+页\)$', '', title_text).strip()
                    full_title = f"{number} {title_text}"
                    titles.append(full_title)
        
        return titles
    
    def append_to_markdown_file(self, title: str, content: str, filename: str):
        """将生成的内容追加到指定的文件"""
        separator = "\n\n" + "="*50 + "\n"
        section_header = f"### {title}\n\n"
        
        # 追加到主输出文件
        with open(filename, "a", encoding="utf-8") as f:
            f.write(separator)
            f.write(section_header)
            f.write(content)
            f.write("\n")
        
        print(f"✓ 已将 '{title}' 的内容追加到 {filename}")
        
        # 保存为单独的MD文件
        self.save_as_individual_md(title, content)
    
    def save_as_individual_md(self, title: str, content: str):
        """将内容保存为单独的MD文件"""
        import re
        
        # 提取编号部分 (如 1.2.1.3.1.1)
        number_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
        if number_match:
            number = number_match.group(1)
            title_name = number_match.group(2)
            
            # 创建文件名: chapter_{编号}._{标题名称}
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
            clean_title = re.sub(r'_+', '_', clean_title)
            clean_title = clean_title.strip('_')
            
            filename = f"chapter_{number}._{clean_title}.md"
        else:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clean_title = re.sub(r'_+', '_', clean_title)
            filename = f"chapter_{clean_title}.md"
        
        # 保存内容到MD文件
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"章节标题: {title}\n")
            if number_match:
                chapter_number = ".".join(number.split(".")[:-1])
                f.write(f"章节编号: {chapter_number}\n")
            else:
                f.write(f"章节编号: 未知\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        print(f"✓ 已保存 '{title}' 到单独文件: {filename}")
    
    async def call_aliyun_api_with_backoff(self, session: aiohttp.ClientSession, prompt: str, attempt: int) -> Optional[str]:
        """带退避策略的API调用"""
        if not self.api_key:
            print("错误: 未设置 ALIYUN_API_KEY 环境变量")
            return None
            
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'qwen-plus',
            'input': {
                'prompt': prompt
            },
            'parameters': {
                'temperature': self.config["api_settings"]["temperature"],
                'max_tokens': self.config["api_settings"]["max_tokens"]
            }
        }
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # 计算延迟时间：基础延迟 + 指数退避 + 随机抖动
        base_delay = 10  # 基础延迟10秒
        exponential_delay = min(base_delay * (2 ** attempt), 120)  # 最大120秒
        jitter = random.uniform(0, 10)  # 0-10秒随机抖动
        total_delay = exponential_delay + jitter
        
        if attempt > 0:
            print(f"⏳ 第{attempt}次重试，等待 {total_delay:.1f} 秒...")
            await asyncio.sleep(total_delay)
        
        try:
            # 更宽松的超时设置
            timeout = aiohttp.ClientTimeout(
                total=self.config["api_settings"]["timeout"],
                connect=60,
                sock_read=120
            )
            
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('output', {}).get('text', '')
                else:
                    error_text = await response.text()
                    print(f"❌ API调用失败: HTTP {response.status}")
                    if response.status == 429:
                        print("⚠ 检测到速率限制，将增加等待时间")
                    return None
                    
        except aiohttp.ClientConnectorError as e:
            print(f"❌ 连接错误: {str(e)}")
            return None
        except asyncio.TimeoutError:
            print("❌ API调用超时")
            return None
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            return None
    
    def create_prompt(self, title: str) -> str:
        """为章节创建提示词"""
        return f"""
作为一名资深的大模型技术专家，请详细扩充以下技术内容：

主题：{title}

要求：
1. 用连续自然段落写作，避免编号列表
2. 保持专业、严谨的技术文档风格
3. 全中文写作，详细介绍技术原理和实现细节
4. 内容详实，至少2000字
5. 风格专业规范，适合技术标书使用

请开始详细阐述："""
    
    async def generate_section_stable(self, session: aiohttp.ClientSession, title: str, index: int, total: int, output_file: str) -> Dict:
        """稳定版章节生成"""
        async with self.semaphore:
            print(f"\n[{index}/{total}] 🚀 开始处理: {title}")
            print(f"🕐 开始时间: {datetime.now().strftime('%H:%M:%S')}")
            
            prompt = self.create_prompt(title)
            
            # 多轮重试机制
            for attempt in range(self.max_retries):
                try:
                    content = await self.call_aliyun_api_with_backoff(session, prompt, attempt)
                    
                    if content and len(content) >= self.min_content_length:
                        print(f"✅ {title} 生成成功 ({len(content)} 字符)")
                        print(f"🕐 完成时间: {datetime.now().strftime('%H:%M:%S')}")
                        
                        # 即时保存
                        self.append_to_markdown_file(title, content, output_file)
                        
                        processing_time = time.time() - getattr(self, 'start_time', time.time())
                        return {
                            "title": title,
                            "content": content,
                            "status": "success",
                            "characters": len(content),
                            "attempts": attempt + 1,
                            "processing_time": processing_time
                        }
                    else:
                        content_length = len(content) if content else 0
                        print(f"❌ {title} 内容不足 ({content_length} 字符)，第{attempt+1}次重试")
                        
                except Exception as e:
                    print(f"❌ {title} 第{attempt+1}次尝试异常: {str(e)}")
            
            print(f"💥 {title} 最终处理失败（已重试{self.max_retries}次）")
            return {
                "title": title,
                "content": "",
                "status": "failed",
                "characters": 0,
                "attempts": self.max_retries
            }
    
    async def process_document_stable(self):
        """稳定版文档处理"""
        # 读取配置
        document_settings = self.config.get("document_settings", {})
        source_file = document_settings.get("source_file", "模型架构.md")
        
        # 生成输出文件名
        file_name, file_ext = os.path.splitext(source_file)
        output_file = f"{file_name}_stable_expanded{file_ext}"
        
        # 读取源文档
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✅ 成功读取源文档: {source_file}")
            print(f"💾 输出文件将保存为: {output_file}")
        except Exception as e:
            print(f"❌ 读取文档失败: {str(e)}")
            return
        
        # 提取标题
        titles = self.extract_all_titles(content, self.title_level)
        print(f"📚 找到 {len(titles)} 个六级标题")
        
        if not titles:
            print("❌ 未找到任何标题")
            return
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=300, connect=60, sock_read=180)
        connector = aiohttp.TCPConnector(
            limit=1,  # 严格限制为1个连接
            limit_per_host=1,
            ttl_dns_cache=600,
            keepalive_timeout=60,
            force_close=False
        )
        
        self.start_time = time.time()
        print("🚀 开始稳定版处理（单线程，高重试）...")
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # 逐个处理，不并发
            results = []
            for i, title in enumerate(titles, 1):
                result = await self.generate_section_stable(session, title, i, len(titles), output_file)
                results.append(result)
                
                # 每处理完一个章节后休息
                if i < len(titles):
                    rest_time = random.uniform(3, 8)  # 3-8秒随机休息
                    print(f"😴 章节间休息 {rest_time:.1f} 秒...")
                    await asyncio.sleep(rest_time)
        
        # 统计结果
        end_time = time.time()
        total_time = end_time - self.start_time
        
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful
        total_chars = sum(r.get("characters", 0) for r in results)
        
        print("\n" + "="*60)
        print("📊 稳定版处理完成统计:")
        print(f"📄 源文档: {source_file}")
        print(f"💾 输出文件: {output_file}")
        print(f"📈 总章节数: {len(titles)}")
        print(f"✅ 成功处理: {successful}")
        print(f"❌ 处理失败: {failed}")
        print(f"🎯 成功率: {successful/len(titles)*100:.1f}%")
        print(f"🔤 总字符数: {total_chars:,}")
        print(f"⏱️ 总耗时: {total_time:.1f}秒")
        if successful > 0:
            print(f"📊 平均每章节: {total_chars/successful:,.0f} 字符")
            print(f"⚡ 平均处理速度: {successful/total_time*3600:.1f} 章节/小时")
        
        # 显示失败详情
        if failed > 0:
            print("\n🔴 失败章节列表:")
            failed_titles = [r.get("title") for r in results if r.get("status") == "failed"]
            for title in failed_titles:
                print(f"  • {title}")

async def main():
    """主函数"""
    print("🐢 稳定版文档扩充工具")
    print("💡 采用单线程+高重试策略，最大化成功率")
    print("="*50)
    
    expander = StableDocumentExpander()
    await expander.process_document_stable()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠ 用户中断操作")
        print("💡 提示: 进度已自动保存，可随时重新运行")
    except Exception as e:
        print(f"\n💥 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()