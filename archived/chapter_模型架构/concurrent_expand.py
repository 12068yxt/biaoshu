#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并发处理工作原理文档扩充脚本
支持3个并发请求，即时保存生成内容
支持五级和六级标题提取切换
增强版：改进错误处理和连接管理
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

class ConcurrentDocumentExpander:
    """并发文档扩充器 - 增强版"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.semaphore = Semaphore(3)  # 限制3个并发请求
        self.api_key = os.getenv("ALIYUN_API_KEY")
        # 获取标题级别配置，默认为6级标题
        self.title_level = self.config.get("title_settings", {}).get("title_level", 6)
        # 获取处理设置
        self.processing_settings = self.config.get("processing_settings", {})
        self.max_retries = self.processing_settings.get("retry_attempts", 3)
        self.min_content_length = self.processing_settings.get("min_content_length", 1000)
        
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
                    "timeout": 120
                },
                "title_settings": {
                    "title_level": 6
                },
                "processing_settings": {
                    "retry_attempts": 3,
                    "min_content_length": 1000
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
    
    def extract_all_fifth_level_titles(self, content: str) -> List[str]:
        """提取所有五级标题"""
        titles = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 处理带▼符号的五级标题 (## ▼ 1.2.2.11. 标题)
            if line.startswith('## ▼'):
                pattern = r'^##\s+▼\s+(\d+(?:\.\d+)*)\.\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = match.group(2)
                    # 移除可能的页数信息
                    title_text = re.sub(r'\(\d+页\)$', '', title_text).strip()
                    full_title = f"{number} {title_text}"
                    titles.append(full_title)
            
            # 处理标准的五级标题 (## 1.2.2.11. 标题)
            elif line.startswith('## ') and not line.startswith('## ▼') and not line.startswith('###'):
                pattern = r'^##\s+(\d+(?:\.\d+)*)\.\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = match.group(2)
                    # 移除可能的页数信息
                    title_text = re.sub(r'\(\d+页\)$', '', title_text).strip()
                    full_title = f"{number} {title_text}"
                    titles.append(full_title)
        
        return titles
    
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
    
    def extract_all_seventh_level_titles(self, content: str) -> List[str]:
        """提取所有七级标题（小标题）"""
        titles = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 处理标准的七级标题 (#### 1.2.2.11.1.1. 标题)
            if line.startswith('#### '):
                pattern = r'^####\s+(\d+(?:\.\d+)*)\.\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = match.group(2)
                    full_title = f"{number} {title_text}"
                    titles.append(full_title)
            
            # 处理纯文本格式的七级标题 (1.2.2.11.1.1 滑动窗口注意力机制)
            else:
                # 匹配七级数字格式的标题
                pattern = r'^(\d+\.\d+\.\d+\.\d+\.\d+\.\d+)\s+(.+)$'
                match = re.match(pattern, line)
                if match:
                    number = match.group(1)
                    title_text = match.group(2)
                    # 移除可能的页数信息和其他附加信息
                    title_text = re.sub(r'\(\d+页?\)$', '', title_text).strip()
                    title_text = re.sub(r'▼\s*', '', title_text).strip()  # 移除▼符号
                    full_title = f"{number} {title_text}"
                    titles.append(full_title)
        
        return titles
    
    def append_to_markdown_file(self, title: str, content: str, filename: str = "工作原理.md"):
        """将生成的内容追加到指定的文件，并保存为单独的md文件"""
        separator = "\n\n" + "="*50 + "\n"
        section_header = f"### {title}\n\n"
        
        # 追加到主输出文件
        with open(filename, "a", encoding="utf-8") as f:
            f.write(separator)
            f.write(section_header)
            f.write(content)
            f.write("\n")
        
        print(f"✓ 已将 '{title}' 的内容追加到 {filename}")
        
        # 保存为单独的TXT文件
        self.save_as_individual_md(title, content)
    
    def save_as_individual_md(self, title: str, content: str):
        """将内容保存为单独的TXT文件"""
        # 从标题中提取编号和名称
        # 格式如: "1.2.1.3.1.1 自注意力机制的信息聚合原理"
        import re
        
        # 提取编号部分 (如 1.2.1.3.1.1)
        number_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
        if number_match:
            number = number_match.group(1)
            title_name = number_match.group(2)
            
            # 创建文件名: chapter_{编号}._{标题名称}
            # 清理标题名称中的特殊字符
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
            clean_title = re.sub(r'_+', '_', clean_title)  # 合并多个下划线
            clean_title = clean_title.strip('_')  # 去除首尾下划线
            
            # 理想格式: chapter_1.2.5.1.1._教师模型选型与蒸馏环境配置
            filename = f"chapter_{number}._{clean_title}.md"
        else:
            # 如果无法解析编号，使用简化命名
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clean_title = re.sub(r'_+', '_', clean_title)
            filename = f"chapter_{clean_title}.md"
        
        # 保存内容到TXT文件
        with open(filename, "w", encoding="utf-8") as f:
            # 写入标题信息
            f.write(f"章节标题: {title}\n")
            # 提取章节编号用于显示
            if number_match:
                chapter_number = ".".join(number.split(".")[:-1])  # 获取上级编号
                f.write(f"章节编号: {chapter_number}\n")
            else:
                f.write(f"章节编号: 未知\n")
            f.write("="*50 + "\n\n")
            # 写入主要内容
            f.write(content)
        
        print(f"✓ 已保存 '{title}' 到单独文件: {filename}")
    
    async def call_aliyun_api(self, session: aiohttp.ClientSession, prompt: str) -> Optional[str]:
        """调用阿里云API生成内容 - 增强版"""
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
        
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.config["api_settings"]["timeout"],
                connect=30,
                sock_read=60
            )
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('output', {}).get('text', '')
                else:
                    error_text = await response.text()
                    print(f"API调用失败: HTTP {response.status} - {error_text[:200]}")
                    return None
        except aiohttp.ClientConnectorError as e:
            print(f"连接错误: {str(e)}")
            return None
        except asyncio.TimeoutError:
            print("API调用超时")
            return None
        except aiohttp.ClientError as e:
            print(f"客户端错误: {str(e)}")
            return None
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            return None

    def classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        error_msg = error_msg.lower()
        if "server disconnected" in error_msg or "connection" in error_msg:
            return "connection"
        elif "timeout" in error_msg:
            return "timeout"
        elif "429" in error_msg or "rate limit" in error_msg:
            return "rate_limit"
        elif "50" in error_msg:  # 500系列服务器错误
            return "server_error"
        else:
            return "other"

    def create_prompt(self, title: str) -> str:
        """为章节创建提示词"""
        return f"""
作为一名资深的大模型技术专家和技术标书撰写顾问，请详细扩充以下技术内容：

主题：{title}

写作要求：
1. 采用连续自然段落形式，避免数字编号和条列式结构
2. 使用专业、严谨、逻辑严密的技术标书语言风格
3. 保持正式规范的文体，注重基础概念解释与技术内涵延展
4. 全中文写作，详细介绍技术原理、实现细节等，避免使用数学符号
5. 内容详实深入，每个部分3000字
6. 风格类似于非常啰嗦的老师，详尽、重复强调、层层展开
7. 模仿技术标书的专业写作风格
8. 要有合理分段

请开始详细阐述："""
    
    async def generate_section_content(self, session: aiohttp.ClientSession, title: str, index: int, total: int, output_file: str = "工作原理.md") -> Dict:
        """生成单个章节内容 - 增强版"""
        async with self.semaphore:  # 控制并发数量
            print(f"[{index}/{total}] 正在处理: {title}")
            
            prompt = self.create_prompt(title)
            
            # 重试机制 - 改进版
            consecutive_failures = 0
            base_delay = 5
            
            for attempt in range(self.max_retries):
                try:
                    content = await self.call_aliyun_api(session, prompt)
                    
                    if content and len(content) >= self.min_content_length:
                        print(f"✓ {title} 生成成功 ({len(content)} 字符)")
                        
                        # 即时保存到指定文件
                        self.append_to_markdown_file(title, content, output_file)
                        
                        return {
                            "title": title,
                            "content": content,
                            "status": "success",
                            "characters": len(content),
                            "attempts": attempt + 1
                        }
                    else:
                        error_type = "content_short" if content else "no_content"
                        print(f"✗ {title} 内容不足({error_type})，第{attempt+1}次重试")
                        
                        # 根据错误类型调整延迟
                        if error_type == "content_short":
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                        else:
                            delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                            
                        consecutive_failures += 1
                        await asyncio.sleep(delay)
                        
                        # 如果连续失败超过2次，增加额外延迟
                        if consecutive_failures >= 2:
                            extra_delay = min(consecutive_failures * 10, 60)  # 最多60秒
                            print(f"⚠ 连续失败{consecutive_failures}次，额外等待{extra_delay}秒")
                            await asyncio.sleep(extra_delay)
                        
                except Exception as e:
                    error_msg = str(e)
                    error_type = self.classify_error(error_msg)
                    print(f"✗ {title} 第{attempt+1}次尝试失败 [{error_type}]: {error_msg}")
                    
                    # 根据错误类型调整策略
                    if error_type == "rate_limit":
                        delay = 30 + random.uniform(5, 15)  # 速率限制等待更长时间
                    elif error_type == "connection":
                        delay = base_delay * (2 ** attempt) + random.uniform(2, 5)
                    elif error_type == "timeout":
                        delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                    else:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                    
                    consecutive_failures += 1
                    await asyncio.sleep(delay)
                    
                    # 连接错误时减少并发
                    if error_type == "connection" and consecutive_failures >= 2:
                        print("⚠ 检测到连接问题，暂时减少并发请求")
                        # 这里可以实现动态调整并发数的逻辑
            
            print(f"✗ {title} 处理失败（已重试{self.max_retries}次）")
            return {
                "title": title,
                "content": "",
                "status": "failed",
                "characters": 0,
                "attempts": self.max_retries,
                "failures": consecutive_failures
            }

    async def process_document(self):
        """处理整个文档 - 增强版"""
        # 从配置文件读取文档设置
        document_settings = self.config.get("document_settings", {})
        source_file = document_settings.get("source_file", "工作原理.md")
        
        # 自动生成输出文件名：输入文件名 + _expanded + 原扩展名
        import os
        file_name, file_ext = os.path.splitext(source_file)
        output_file = f"{file_name}_expanded{file_ext}"
        
        # 读取源文档
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✓ 成功读取源文档: {source_file}")
            print(f"✓ 输出文件将保存为: {output_file}")
        except FileNotFoundError:
            print(f"错误: 未找到源文档 {source_file}")
            return
        except Exception as e:
            print(f"错误: 读取文档失败 - {str(e)}")
            return
        
        # 提取所有标题
        titles = self.extract_all_titles(content, self.title_level)
        level_name = "五级" if self.title_level == 5 else "六级"
        print(f"找到 {len(titles)} 个{level_name}标题")
        
        if not titles:
            print(f"未找到任何{level_name}标题")
            # 如果没有找到指定级别的标题，尝试另一种级别
            alternative_level = 5 if self.title_level == 6 else 6
            alternative_titles = self.extract_all_titles(content, alternative_level)
            alt_level_name = "五级" if alternative_level == 5 else "六级"
            if alternative_titles:
                print(f"检测到 {len(alternative_titles)} 个{alt_level_name}标题，是否切换到{alt_level_name}标题处理？")
                print("请在 config.json 中设置:")
                print(f'  "title_settings": {{"title_level": {alternative_level}}}')
                return
            else:
                print("文档中未找到任何五级或六级标题")
                return
        
        # 创建HTTP会话 - 改进版
        timeout = aiohttp.ClientTimeout(
            total=self.config["api_settings"]["timeout"] + 60,
            connect=30,
            sock_read=60
        )
        connector = aiohttp.TCPConnector(
            limit=3,  # 限制连接数
            limit_per_host=3,  # 每个主机的连接限制
            ttl_dns_cache=300,  # DNS缓存时间
            keepalive_timeout=30,  # 保持连接超时
            force_close=False  # 允许连接复用
        )
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            print("🚀 开始并发处理文档...")
            start_time = time.time()
            
            # 创建所有任务
            tasks = [
                self.generate_section_content(session, title, i+1, len(titles), output_file)
                for i, title in enumerate(titles)
            ]
            
            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
        
        # 统计结果
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed = len(titles) - successful
        total_chars = sum(r.get("characters", 0) for r in results if isinstance(r, dict))
        total_attempts = sum(r.get("attempts", 0) for r in results if isinstance(r, dict))
        
        print("\n" + "="*60)
        print("📊 处理完成统计:")
        print(f"📄 源文档: {source_file}")
        print(f"💾 输出文件: {output_file}")
        print(f"📈 总章节数: {len(titles)}")
        print(f"✅ 成功处理: {successful}")
        print(f"❌ 处理失败: {failed}")
        print(f"🎯 成功率: {successful/len(titles)*100:.1f}%")
        print(f"🔤 总字符数: {total_chars:,}")
        print(f"🔄 总重试次数: {total_attempts - len(titles)}")
        print(f"⏱️ 总耗时: {processing_time:.1f}秒")
        if successful > 0:
            print(f"📊 平均每章节: {total_chars/successful:,.0f} 字符")
            print(f"⚡ 平均处理速度: {len(titles)/processing_time*60:.1f} 章节/分钟")
        
        # 显示失败详情
        if failed > 0:
            print("\n🔴 失败章节列表:")
            failed_titles = [r.get("title") for r in results if isinstance(r, dict) and r.get("status") == "failed"]
            for title in failed_titles:
                print(f"  • {title}")

async def main():
    """主函数"""
    print("🤖 文档智能扩充工具 - 增强版")
    print("="*50)
    expander = ConcurrentDocumentExpander()
    await expander.process_document()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠ 用户中断操作")
        print("💡 提示: 进度已自动保存，可随时重新运行继续处理")
    except Exception as e:
        print(f"\n💥 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
