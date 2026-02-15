#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小标题处理器
专门处理文档中的深层级小标题内容生成
"""

import asyncio
import aiohttp
import json
import os
import re
from typing import List, Dict, Optional
from concurrent_expand import ConcurrentDocumentExpander

class SubtitleProcessor:
    """小标题处理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.expander = ConcurrentDocumentExpander(config_file)
        self.subtitle_level = 7  # 默认处理七级标题
        
    def create_detailed_prompt(self, title: str, parent_context: str = "") -> str:
        """为小标题创建详细的提示词"""
        base_prompt = f"""
作为一名资深的大模型技术专家和技术标书撰写顾问，请详细扩充以下技术小节内容：

小节主题：{title}
{'上级章节背景：' + parent_context if parent_context else ''}

详细写作要求：
1. 采用连续自然段落形式，避免数字编号和条列式结构
2. 使用专业、严谨、逻辑严密的技术标书语言风格
3. 保持正式规范的文体，注重基础概念解释与技术内涵延展
4. 全中文写作，详细介绍技术原理、实现细节、算法流程等
5. 内容详实深入，每个小节2000-3000字
6. 风格类似于非常啰嗦的老师，详尽、重复强调、层层展开
7. 需要包含具体的技术实现步骤、关键参数设置、注意事项等
8. 可以加入实际应用案例、性能对比、优缺点分析等内容

请开始详细阐述该技术小节的具体内容："""
        
        return base_prompt
    
    def group_subtitles_by_parent(self, subtitles: List[str]) -> Dict[str, List[str]]:
        """将小标题按父级标题分组"""
        groups = {}
        
        for subtitle in subtitles:
            # 提取编号部分
            number_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', subtitle)
            if number_match:
                full_number = number_match.group(1)
                title_text = number_match.group(2)
                
                # 获取父级编号（去掉最后一级）
                number_parts = full_number.split('.')
                if len(number_parts) > 1:
                    parent_number = '.'.join(number_parts[:-1])
                    parent_key = f"{parent_number} *"
                    
                    if parent_key not in groups:
                        groups[parent_key] = []
                    groups[parent_key].append(subtitle)
        
        return groups
    
    async def generate_subtitle_content(self, session: aiohttp.ClientSession, 
                                      subtitle: str, parent_context: str = "", 
                                      index: int = 0, total: int = 0) -> Dict:
        """生成单个小标题内容"""
        async with self.expander.semaphore:
            print(f"[{index}/{total}] 正在处理小标题: {subtitle}")
            
            prompt = self.create_detailed_prompt(subtitle, parent_context)
            
            # 重试机制
            for attempt in range(3):
                try:
                    content = await self.expander.call_aliyun_api(session, prompt)
                    if content and len(content) > 800:  # 小标题内容要求稍低
                        print(f"✓ {subtitle} 生成成功 ({len(content)} 字符)")
                        
                        # 保存内容
                        self.save_subtitle_content(subtitle, content, parent_context)
                        
                        return {
                            "title": subtitle,
                            "content": content,
                            "status": "success",
                            "characters": len(content),
                            "parent_context": parent_context
                        }
                    else:
                        print(f"✗ {subtitle} 内容不足，第{attempt+1}次重试")
                        await asyncio.sleep(2 ** attempt * 3)  # 较短的等待时间
                        
                except Exception as e:
                    print(f"✗ {subtitle} 第{attempt+1}次尝试失败: {str(e)}")
                    await asyncio.sleep(2 ** attempt * 3)
            
            print(f"✗ {subtitle} 处理失败")
            return {
                "title": subtitle,
                "content": "",
                "status": "failed",
                "characters": 0,
                "parent_context": parent_context
            }
    
    def save_subtitle_content(self, title: str, content: str, parent_context: str = ""):
        """保存小标题内容"""
        # 从标题中提取编号
        number_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', title)
        if number_match:
            number = number_match.group(1)
            title_name = number_match.group(2)
            
            # 创建文件名
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title_name)
            clean_title = re.sub(r'_+', '_', clean_title).strip('_')
            filename = f"subtitle_{number.replace('.', '_')}.{clean_title}.md"
        else:
            clean_title = re.sub(r'[^\w\u4e00-\u9fff\-_]', '_', title)
            clean_title = re.sub(r'_+', '_', clean_title)
            filename = f"subtitle_{clean_title}.md"
        
        # 保存内容
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            if parent_context:
                f.write(f"**所属章节**: {parent_context}\n\n")
            f.write("---\n\n")
            f.write(content)
        
        print(f"✓ 已保存小标题内容到: {filename}")
    
    async def process_all_subtitles(self):
        """处理文档中的所有小标题"""
        # 读取源文档
        document_settings = self.expander.config.get("document_settings", {})
        source_file = document_settings.get("source_file", "模型架构.md")
        
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✓ 成功读取源文档: {source_file}")
        except FileNotFoundError:
            print(f"错误: 未找到源文档 {source_file}")
            return
        except Exception as e:
            print(f"错误: 读取文档失败 - {str(e)}")
            return
        
        # 提取七级标题（小标题）
        subtitles = self.expander.extract_all_seventh_level_titles(content)
        print(f"找到 {len(subtitles)} 个小标题")
        
        if not subtitles:
            print("未找到任何小标题")
            return
        
        # 按父级分组
        grouped_subtitles = self.group_subtitles_by_parent(subtitles)
        print(f"按父级章节分组为 {len(grouped_subtitles)} 组")
        
        # 显示分组信息
        print("\n分组详情:")
        for parent, sub_list in list(grouped_subtitles.items())[:3]:  # 显示前3组
            print(f"  {parent}: {len(sub_list)} 个小标题")
            for subtitle in sub_list[:2]:  # 显示每组前2个小标题
                print(f"    - {subtitle}")
            if len(sub_list) > 2:
                print(f"    ... 还有 {len(sub_list) - 2} 个小标题")
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=self.expander.config["api_settings"]["timeout"] + 30)
        connector = aiohttp.TCPConnector(limit=3)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            # 为每个分组创建任务
            all_tasks = []
            task_index = 1
            
            for parent_title, subtitle_list in grouped_subtitles.items():
                # 获取父级标题的上下文
                parent_context = self.get_parent_context(content, parent_title)
                
                # 为每个小标题创建任务
                for subtitle in subtitle_list:
                    task = self.generate_subtitle_content(
                        session, subtitle, parent_context, task_index, len(subtitles)
                    )
                    all_tasks.append(task)
                    task_index += 1
            
            # 并发执行所有任务
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # 统计结果
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed = len(subtitles) - successful
        total_chars = sum(r.get("characters", 0) for r in results if isinstance(r, dict))
        
        print("\n" + "="*50)
        print("小标题处理完成统计:")
        print(f"源文档: {source_file}")
        print(f"总小标题数: {len(subtitles)}")
        print(f"成功处理: {successful}")
        print(f"处理失败: {failed}")
        print(f"成功率: {successful/len(subtitles)*100:.1f}%")
        print(f"总字符数: {total_chars:,}")
        if successful > 0:
            print(f"平均每个小标题: {total_chars/successful:,.0f} 字符")
    
    def get_parent_context(self, content: str, parent_key: str) -> str:
        """获取父级标题的上下文信息"""
        # 从parent_key中提取编号
        parent_number = parent_key.replace(' *', '')
        
        # 在文档中查找对应的父级标题
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(parent_number):
                return line
        return ""

async def main():
    """主函数"""
    processor = SubtitleProcessor()
    await processor.process_all_subtitles()

if __name__ == "__main__":
    asyncio.run(main())