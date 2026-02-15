#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT兼容SVG技术图表生成器
专门为技术文档生成黑白线框风格的流程图、架构图等
支持提示词调试和批量处理章节文件
"""

import os
import json
import re
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('svg_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PPTSVGGenerator:
    def __init__(self, config_path: str = "svg_config.json"):
        """初始化SVG生成器"""
        self.config_path = config_path
        self.config = self.load_config()
        self.output_dir = Path("../generated_svgs")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化进度跟踪
        self.progress_file = Path("../svg_generation_progress.json")
        self.progress = self.load_progress()
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_path} 未找到，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "prompts": {
                "flowchart": {
                    "template": "请为以下技术内容创建一个清晰的流程图SVG：\n\n内容主题: {title}\n技术要点: {content}\n\n要求:\n1. 使用标准SVG格式，尺寸1920x1080\n2. 采用黑白线框风格，线条粗细2-3px\n3. 使用矩形、菱形、圆形等基本形状\n4. 添加箭头表示流程方向\n5. 在节点内添加简洁的文字标签\n6. 保持整体布局清晰，易于理解\n7. 使用标准的流程图符号\n8. 返回纯SVG代码，无需解释",
                    "diagram_types": ["流程图", "工作流", "算法流程"]
                },
                "architecture": {
                    "template": "请为以下技术架构创建架构图SVG：\n\n系统名称: {title}\n架构描述: {content}\n\n要求:\n1. 标准SVG格式，1920x1080尺寸\n2. 黑白线框风格，专业简洁\n3. 使用矩形表示组件，连线表示关系\n4. 层次化布局，体现系统架构\n5. 添加组件标签和接口标识\n6. 使用虚线表示可选组件\n7. 保持整体平衡美观\n8. 返回纯SVG代码",
                    "diagram_types": ["系统架构", "网络拓扑", "软件架构"]
                },
                "data_flow": {
                    "template": "请创建数据流向图SVG：\n\n主题: {title}\n数据流描述: {content}\n\n要求:\n1. 标准SVG格式，1920x1080\n2. 黑白线框风格\n3. 使用箭头表示数据流向\n4. 圆形或矩形表示数据节点\n5. 不同线型表示不同类型的数据流\n6. 添加数据标签和处理节点\n7. 清晰展现数据处理过程\n8. 返回纯SVG代码",
                    "diagram_types": ["数据流", "信息流", "处理流程"]
                }
            },
            "default_style": {
                "stroke_width": "2",
                "stroke_color": "#000000",
                "fill_color": "none",
                "font_family": "Arial, sans-serif",
                "font_size": "16"
            }
        }
    
    def load_progress(self) -> Dict:
        """加载进度文件"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    # 确保必要的键存在
                    if 'completed' not in progress_data:
                        progress_data['completed'] = []
                    if 'failed' not in progress_data:
                        progress_data['failed'] = []
                    return progress_data
            except Exception as e:
                logger.warning(f"加载进度文件失败: {e}")
                pass
        return {"completed": [], "failed": []}
    
    def save_progress(self):
        """保存进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def extract_chapter_info(self, filename: str) -> Tuple[str, str]:
        """从文件名提取章节编号和标题"""
        # 匹配格式: chapter_01_1.2.1.3.1.1 标题内容.txt
        pattern = r'chapter_(\d+)_(\d+(?:\.\d+)*)\s+(.+)\.txt'
        match = re.match(pattern, filename)
        if match:
            chapter_num = match.group(1)
            section_id = match.group(2)
            title = match.group(3)
            return f"{section_id} {title}", f"chapter_{chapter_num}"
        return filename.replace('.txt', ''), filename.replace('.txt', '')
    
    def read_chapter_content(self, file_path: Path) -> str:
        """读取章节内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取主要内容（跳过标题行）
            lines = content.split('\n')
            main_content = []
            content_started = False
            
            for line in lines:
                if line.strip() == '=' * 50:
                    content_started = True
                    continue
                if content_started and line.strip():
                    main_content.append(line.strip())
            
            return '\n'.join(main_content[:1000])  # 限制长度避免过长
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败: {e}")
            return ""
    
    def select_diagram_type(self, title: str, content: str) -> str:
        """根据内容自动选择图表类型"""
        content_lower = content.lower()
        title_lower = title.lower()
        
        # 关键词匹配
        flow_keywords = ['流程', '步骤', '过程', '阶段', '顺序', 'pipeline', 'algorithm']
        arch_keywords = ['架构', '系统', '组件', '模块', '结构', 'framework', 'system']
        data_keywords = ['数据', '信息', '流向', '传输', '处理', 'data', 'flow']
        
        # 统计关键词出现次数
        flow_score = sum(content_lower.count(kw) + title_lower.count(kw) for kw in flow_keywords)
        arch_score = sum(content_lower.count(kw) + title_lower.count(kw) for kw in arch_keywords)
        data_score = sum(content_lower.count(kw) + title_lower.count(kw) for kw in data_keywords)
        
        scores = {'flowchart': flow_score, 'architecture': arch_score, 'data_flow': data_score}
        return max(scores, key=scores.get)
    
    def generate_prompt(self, diagram_type: str, title: str, content: str) -> str:
        """生成AI提示词"""
        if diagram_type not in self.config['prompts']:
            diagram_type = 'flowchart'  # 默认使用流程图
        
        template = self.config['prompts'][diagram_type]['template']
        return template.format(title=title, content=content)
    
    async def call_qwen_api(self, prompt: str) -> Optional[str]:
        """调用通义千问API生成SVG"""
        try:
            import aiohttp
            import os
            
            api_key = os.getenv('ALIYUN_API_KEY')
            if not api_key:
                logger.error("未设置 ALIYUN_API_KEY 环境变量")
                return None
            
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen-plus",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_tokens": 2000
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['output']['text']
                    else:
                        error_text = await response.text()
                        logger.error(f"API调用失败: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"API调用异常: {e}")
            return None
    
    def validate_svg(self, svg_content: str) -> bool:
        """验证SVG内容的基本有效性"""
        if not svg_content:
            return False
        
        # 检查基本SVG结构
        svg_content = svg_content.strip()
        if not (svg_content.startswith('<svg') and svg_content.endswith('</svg>')):
            return False
        
        # 检查尺寸
        if 'width="1920"' not in svg_content or 'height="1080"' not in svg_content:
            logger.warning("SVG尺寸可能不符合PPT标准(1920x1080)")
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
        clean_name = re.sub(illegal_chars, '_', filename)
        # 限制长度
        if len(clean_name) > 100:
            clean_name = clean_name[:100]
        return clean_name
    
    async def generate_single_svg(self, chapter_file: Path, debug_mode: bool = False) -> bool:
        """生成单个章节的SVG"""
        try:
            # 检查是否已完成
            file_key = str(chapter_file.relative_to(Path("../chapter_1.2.1.3")))
            if file_key in self.progress["completed"]:
                logger.info(f"跳过已完成的文件: {file_key}")
                return True
            
            # 提取章节信息
            title, chapter_id = self.extract_chapter_info(chapter_file.name)
            logger.info(f"处理章节: {title}")
            
            # 读取内容
            content = self.read_chapter_content(chapter_file)
            if not content:
                logger.error(f"无法读取内容: {chapter_file}")
                self.progress["failed"].append(file_key)
                return False
            
            # 选择图表类型
            diagram_type = self.select_diagram_type(title, content)
            logger.info(f"选择图表类型: {diagram_type}")
            
            # 生成提示词
            prompt = self.generate_prompt(diagram_type, title, content)
            
            # 调试模式下只显示提示词
            if debug_mode:
                print("=" * 80)
                print(f"章节: {title}")
                print(f"图表类型: {diagram_type}")
                print("提示词:")
                print(prompt)
                print("=" * 80)
                return True
            
            # 调用API生成SVG
            logger.info("调用AI API生成SVG...")
            svg_result = await self.call_qwen_api(prompt)
            
            if not svg_result:
                logger.error("API调用失败")
                self.progress["failed"].append(file_key)
                return False
            
            # 验证SVG
            if not self.validate_svg(svg_result):
                logger.warning("生成的SVG可能无效，但仍保存")
            
            # 保存SVG文件
            safe_title = self.sanitize_filename(title)
            svg_filename = f"{chapter_id}_{safe_title}.svg"
            svg_path = self.output_dir / svg_filename
            
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_result)
            
            logger.info(f"SVG已保存: {svg_path}")
            
            # 更新进度
            self.progress["completed"].append(file_key)
            self.save_progress()
            
            return True
            
        except Exception as e:
            logger.error(f"处理文件 {chapter_file} 时出错: {e}")
            self.progress["failed"].append(str(chapter_file.relative_to(Path("../chapter_1.2.1.3"))))
            return False
    
    async def generate_batch_svgs(self, chapter_dir: str = "../chapter_1.2.1.3", 
                                max_concurrent: int = 3, debug_mode: bool = False):
        """批量生成SVG"""
        chapter_path = Path(chapter_dir)
        if not chapter_path.exists():
            logger.error(f"章节目录不存在: {chapter_dir}")
            return
        
        # 获取所有章节文件
        txt_files = list(chapter_path.glob("*.txt"))
        txt_files.sort()  # 按文件名排序
        
        logger.info(f"找到 {len(txt_files)} 个章节文件")
        
        if debug_mode:
            # 调试模式下只处理前3个文件
            txt_files = txt_files[:3]
            logger.info("调试模式: 只处理前3个文件")
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.generate_single_svg(file_path, debug_mode)
        
        # 并发处理
        tasks = [process_with_semaphore(file_path) for file_path in txt_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for result in results if result is True)
        failed_count = len(results) - success_count
        
        logger.info(f"处理完成: 成功 {success_count}, 失败 {failed_count}")
        if self.progress["failed"]:
            logger.info(f"失败文件: {self.progress['failed']}")
    
    def list_available_prompts(self):
        """列出可用的提示词模板"""
        print("\n可用的图表类型和提示词:")
        print("=" * 50)
        for diagram_type, config in self.config['prompts'].items():
            print(f"\n类型: {diagram_type}")
            print(f"适用场景: {', '.join(config['diagram_types'])}")
            print("提示词模板:")
            print(config['template'][:200] + "..." if len(config['template']) > 200 else config['template'])
            print("-" * 30)
    
    def test_single_prompt(self, diagram_type: str, title: str, content: str):
        """测试单个提示词"""
        if diagram_type not in self.config['prompts']:
            print(f"错误: 不支持的图表类型 '{diagram_type}'")
            print("支持的类型:", list(self.config['prompts'].keys()))
            return
        
        prompt = self.generate_prompt(diagram_type, title, content)
        print("=" * 80)
        print(f"图表类型: {diagram_type}")
        print(f"标题: {title}")
        print("生成的提示词:")
        print(prompt)
        print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="PPT兼容SVG技术图表生成器")
    parser.add_argument("--mode", choices=["batch", "debug", "test"], 
                       default="batch", help="运行模式")
    parser.add_argument("--chapter-dir", default="../chapter_1.2.1.3", 
                       help="章节文件目录")
    parser.add_argument("--diagram-type", choices=["flowchart", "architecture", "data_flow"],
                       help="指定图表类型(测试模式用)")
    parser.add_argument("--title", help="测试标题(测试模式用)")
    parser.add_argument("--content", help="测试内容(测试模式用)")
    parser.add_argument("--list-prompts", action="store_true", 
                       help="列出所有可用提示词")
    parser.add_argument("--max-concurrent", type=int, default=3, 
                       help="最大并发数")
    
    args = parser.parse_args()
    
    generator = PPTSVGGenerator()
    
    if args.list_prompts:
        generator.list_available_prompts()
        return
    
    if args.mode == "test":
        if not all([args.diagram_type, args.title, args.content]):
            print("测试模式需要提供 --diagram-type, --title, --content 参数")
            return
        generator.test_single_prompt(args.diagram_type, args.title, args.content)
        return
    
    # 运行批量或调试模式
    debug_mode = (args.mode == "debug")
    
    try:
        asyncio.run(generator.generate_batch_svgs(
            chapter_dir=args.chapter_dir,
            max_concurrent=args.max_concurrent,
            debug_mode=debug_mode
        ))
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()