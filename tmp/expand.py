#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版大模型技术标书内容扩充脚本
支持多种API提供商，具备完善的错误处理和重试机制
"""

import asyncio
import json
import os
import time
import random
from typing import List, Dict, Tuple, Optional
import aiohttp
import logging
from datetime import datetime
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('expansion_detailed_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API配置类"""
    provider: str
    api_key: str
    model: str
    base_url: str
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 300

class AdvancedContentExpander:
    """高级内容扩充器"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化扩充器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.api_configs = self._setup_api_configs()
        self.retry_count = 5  # 增加重试次数
        self.backoff_base = 5  # 增加重试间隔时间
        self.concurrent_limit = 1  # 保持低并发
        
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_file} 未找到，使用默认配置")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "api_settings": {
                "providers": [
                    {
                        "name": "aliyun",
                        "api_key_env": "ALIYUN_API_KEY",
                        "model": "qwen-plus",
                        "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                    },
                    {
                        "name": "openai",
                        "api_key_env": "OPENAI_API_KEY", 
                        "model": "gpt-3.5-turbo",
                        "base_url": "https://api.openai.com/v1/chat/completions"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 300,
                "concurrent_limit": 3
            },
            "content_settings": {
                "target_word_count": {"min": 3000, "max": 4000},
                "writing_style": "technical_specification"
            }
        }
    
    def _setup_api_configs(self) -> List[APIConfig]:
        """设置API配置"""
        configs = []
        providers = self.config.get("api_settings", {}).get("providers", [])
        
        for provider in providers:
            api_key = os.getenv(provider["api_key_env"])
            if api_key:
                configs.append(APIConfig(
                    provider=provider["name"],
                    api_key=api_key,
                    model=provider["model"],
                    base_url=provider["base_url"],
                    temperature=self.config["api_settings"].get("temperature", 0.7),
                    max_tokens=self.config["api_settings"].get("max_tokens", 4000),
                    timeout=self.config["api_settings"].get("timeout", 300)
                ))
            else:
                logger.warning(f"未找到 {provider['name']} 的API密钥")
        
        if not configs:
            logger.warning("未配置任何有效的API提供商")
        
        return configs
    
    def _get_expansion_prompt(self, section_title: str) -> str:
        """获取扩充提示词"""
        return f"""
作为一名资深的大模型技术专家和技术标书撰写顾问，请详细扩充以下技术内容：

章节标题：{section_title}

写作要求：
1. 采用连续自然段落形式，避免数字编号和条列式结构
2. 使用专业、严谨、逻辑严密的技术标书语言风格
3. 保持正式规范的文体，注重基础概念解释与技术内涵延展
4. 全中文写作，详细介绍技术原理、实现细节等，避免使用数学符号，数学公式
5. 内容详实深入，每个部分3000-4000字
6. 风格类似于非常啰嗦的老师，即详尽、重复强调、层层展开，确保信息密度高且表述完整
7. 模仿技术标书的专业写作风格，注重术语解释、概念延展与技术深度


"""

    async def _call_single_api(self, session: aiohttp.ClientSession, config: APIConfig, 
                              section_title: str, prompt: str) -> Optional[str]:
        """调用单个API"""
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 根据不同提供商使用不同的请求格式
        if config.provider == "aliyun":
            payload = {
                'model': config.model,
                'input': {
                    'prompt': prompt
                },
                'parameters': {
                    'temperature': config.temperature,
                    'max_tokens': config.max_tokens
                }
            }
        else:  # openai格式
            payload = {
                'model': config.model,
                'messages': [
                    {'role': 'system', 'content': '你是一位资深的大模型技术专家和军事技术标书撰写顾问'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': config.temperature,
                'max_tokens': config.max_tokens
            }
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            async with session.post(config.base_url, headers=headers, 
                                  json=payload, timeout=timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    # 处理不同API的响应格式
                    if config.provider == "aliyun":
                        return result.get('output', {}).get('text', '')
                    elif config.provider == "openai":
                        return result.get('choices', [{}])[0].get('message', {}).get('content', '')
                else:
                    error_text = await response.text()
                    logger.error(f"{config.provider} API调用失败: {response.status}, 错误信息: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"{config.provider} API调用超时")
            return None
        except Exception as e:
            logger.error(f"{config.provider} API调用异常: {str(e)}")
            return None

    async def call_api_with_retry(self, session: aiohttp.ClientSession, 
                                section_title: str) -> Tuple[str, str]:
        """带重试机制的API调用"""
        prompt = self._get_expansion_prompt(section_title)
        
        for attempt in range(self.retry_count):
            # 随机选择API提供商
            random.shuffle(self.api_configs)
            
            for config in self.api_configs:
                logger.info(f"尝试使用 {config.provider} 生成内容: {section_title[:30]}... (第{attempt+1}次)")
                
                content = await self._call_single_api(session, config, section_title, prompt)
                
                if content and len(content.strip()) > 1000:  # 确保内容足够长
                    logger.info(f"成功生成内容: {section_title[:30]}...")
                    return section_title, content
                
                logger.warning(f"{config.provider} 生成内容不足，尝试下一个提供商")
            
            # 如果所有提供商都失败，等待后重试
            if attempt < self.retry_count - 1:
                wait_time = self.backoff_base ** attempt + random.uniform(0, 1)
                logger.info(f"第{attempt+1}次尝试失败，等待 {wait_time:.1f} 秒后重试...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"所有尝试均失败: {section_title}")
        return section_title, ""

    async def expand_sections_parallel(self, sections: List[str]) -> Dict[str, str]:
        """并行扩充多个章节"""
        logger.info(f"开始并行扩充 {len(sections)} 个章节")
        
        semaphore = asyncio.Semaphore(self.config["api_settings"].get("concurrent_limit", 3))
        
        async def bounded_call(section):
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    return await self.call_api_with_retry(session, section)
        
        # 并发执行所有章节的扩充
        tasks = [bounded_call(section) for section in sections]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        expanded_content = {}
        for i, result in enumerate(results):
            if isinstance(result, tuple) and len(result) == 2:
                title, content = result
                if content.strip():
                    expanded_content[title] = content
                else:
                    logger.warning(f"章节 '{sections[i]}' 内容为空")
            elif isinstance(result, Exception):
                logger.error(f"章节 '{sections[i]}' 处理异常: {result}")
            else:
                logger.error(f"章节 '{sections[i]}' 返回无效结果")
        
        logger.info(f"完成扩充，成功生成 {len(expanded_content)} 个章节")
        return expanded_content

    def _extract_all_sections_from_document(self) -> List[str]:
        """从工作原理.md文件中提取所有章节标题"""
        try:
            with open("工作原理.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用正则表达式匹配章节标题格式
            import re
            
            # 匹配各种可能的章节标题格式
            patterns = [
                r'^#{1,6}\s+(.+)$',  # Markdown标题
                r'^(\d+\.\d+(?:\.\d+)*)\s+(.+)$',  # 数字编号标题
                r'^([A-Z][^.]+)\s*\.{2,}\s*(.+)$',  # 带点的标题
            ]
            
            sections = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 检查各种模式
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        if len(patterns) == 3 and pattern == patterns[1]:  # 数字编号模式
                            full_title = f"{match.group(1)} {match.group(2)}"
                        elif len(patterns) == 3 and pattern == patterns[2]:  # 带点模式
                            full_title = f"{match.group(1)} {match.group(2)}"
                        else:
                            full_title = match.group(1)
                        
                        # 过滤掉太短或明显不是章节标题的内容
                        if len(full_title) > 10 and not full_title.startswith(('---', '===', '```')):
                            sections.append(full_title)
                        break
            
            # 去重并排序
            unique_sections = list(dict.fromkeys(sections))
            logger.info(f"从文档中提取到 {len(unique_sections)} 个章节标题")
            return unique_sections[:50]  # 限制最大数量避免过度处理
            
        except FileNotFoundError:
            logger.error("未找到工作原理.md文件")
            return []
        except Exception as e:
            logger.error(f"读取文档时出错: {str(e)}")
            return []

    def integrate_with_working_principle_document(self, expanded_content: Dict[str, str]) -> str:
        """专门为工作原理.md文件整合扩充内容"""
        try:
            original_file = "工作原理.md"
            
            # 检查原始文件是否存在
            if not os.path.exists(original_file):
                logger.info("工作原理.md 文件不存在，创建新文件")
                # 创建新的工作原理.md文件
                with open(original_file, 'w', encoding='utf-8') as f:
                    f.write("# 大模型工作原理技术说明\n\n")
                    f.write("本文档详细阐述大模型的核心工作机制和技术原理。\n\n")
                    f.write("---\n\n")
                
                # 读取刚创建的文件
                with open(original_file, 'r', encoding='utf-8') as f:
                    original_lines = f.readlines()
            else:
                # 读取现有文档
                with open(original_file, 'r', encoding='utf-8') as f:
                    original_lines = f.readlines()
                
                # 创建备份
                backup_file = f"{original_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.writelines(original_lines)
                logger.info(f"原始文档已备份至: {backup_file}")
            
            # 准备输出内容
            output_lines = []
            
            # 保留原有内容的开头部分
            header_end_index = 0
            for i, line in enumerate(original_lines):
                if line.strip() == "---":
                    header_end_index = i + 1
                    break
            
            # 添加头部内容
            output_lines.extend(original_lines[:header_end_index])
            
            # 为每个扩充的章节添加内容
            for section_title, content in expanded_content.items():
                # 添加章节标题
                output_lines.append(f"\n## {section_title}\n\n")
                
                # 格式化内容，确保以自然段落形式呈现
                formatted_content = '\n'.join([
                    f"{para.strip()}" for para in content.split('\n') 
                    if para.strip() and not para.strip().startswith('#')
                ])
                output_lines.append(formatted_content)
                output_lines.append('\n\n')
                output_lines.append('---\n\n')  # 章节分隔线
            
            # 写入更新后的文档
            with open(original_file, 'w', encoding='utf-8') as f:
                f.writelines(output_lines)
            
            logger.info(f"工作原理文档更新完成: {original_file}")
            return original_file
            
        except Exception as e:
            logger.error(f"工作原理文档整合失败: {str(e)}")
            return ""

def main():
    """主函数 - 专门用于填充工作原理.md"""
    logger.info("启动工作原理文档智能填充程序")
    
    # 初始化扩充器
    expander = AdvancedContentExpander()
    
    if not expander.api_configs:
        logger.error("未配置有效的API提供商，请检查环境变量和配置文件")
        return
    
    # 从配置文件读取要扩展的章节
    sections_config = expander.config.get("sections_to_expand", [])
    
    if sections_config == [] or sections_config == ["*"]:
        # 如果配置为空数组或通配符，读取工作原理.md中的所有章节
        logger.info("检测到全章节扩展模式，正在分析工作原理.md文件...")
        target_sections = expander._extract_all_sections_from_document()
    else:
        # 使用配置文件中指定的具体章节
        target_sections = sections_config
    
    if not target_sections:
        logger.error("未找到任何待填充的章节")
        return
        
    logger.info(f"待填充的工作原理章节 ({len(target_sections)}个):")
    for i, section in enumerate(target_sections, 1):
        logger.info(f"  {i}. {section}")
    
    # 执行并行扩充
    start_time = time.time()
    
    try:
        expanded_content = asyncio.run(expander.expand_sections_parallel(target_sections))
        
        if expanded_content:
            # 专门为工作原理.md整合内容
            output_file = expander.integrate_with_working_principle_document(expanded_content)
            
            # 生成详细的统计报告
            end_time = time.time()
            total_chars = sum(len(content) for content in expanded_content.values())
            avg_chars_per_section = total_chars / len(expanded_content)
            
            print("\n" + "="*60)
            print("工作原理文档智能填充完成报告")
            print("="*60)
            print(f"预设章节数量: {len(target_sections)}")
            print(f"成功填充章节: {len(expanded_content)}")
            print(f"填充成功率: {len(expanded_content)/len(target_sections)*100:.1f}%")
            print(f"总字符数: {total_chars:,}")
            print(f"平均每章节字符数: {avg_chars_per_section:,.0f}")
            print(f"总耗时: {end_time - start_time:.2f} 秒")
            print(f"平均每章节耗时: {(end_time - start_time)/len(target_sections):.2f} 秒")
            print(f"输出文件: {output_file}")
            print("="*60)
            
            # 显示各章节详情
            print("\n各章节填充详情:")
            print("-" * 40)
            for title, content in expanded_content.items():
                char_count = len(content)
                print(f"✓ {title[:30]}... ({char_count:,} 字符)")
            
        else:
            logger.error("未能生成任何填充内容")
            
    except KeyboardInterrupt:
        logger.info("用户中断程序执行")
    except Exception as e:
        logger.error(f"程序执行异常: {str(e)}")

if __name__ == "__main__":
    main()