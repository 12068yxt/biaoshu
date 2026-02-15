#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版PPT SVG生成器
专注于为技术文档生成PPT兼容的SVG图表
"""

import os
import json
import re
import asyncio
import aiohttp
from typing import List, Tuple
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleSVGGenerator:
    def __init__(self):
        """初始化生成器"""
        self.api_key = os.getenv('ALIYUN_API_KEY')
        if not self.api_key:
            raise ValueError("请设置环境变量 ALIYUN_API_KEY")
        
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 创建输出目录
        self.output_dir = "generated_svgs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 进度跟踪
        self.completed_files = set()
        self.progress_file = "svg_progress.json"
        self.load_progress()
    
    def load_progress(self):
        """加载处理进度"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.completed_files = set(data.get('completed', []))
    
    def save_progress(self):
        """保存处理进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'completed': list(self.completed_files),
                'updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def get_chapter_files(self) -> List[str]:
        """获取所有章节文件"""
        files = [f for f in os.listdir('.') if f.startswith('chapter_') and f.endswith('.txt')]
        files.sort()
        return [f for f in files if f not in self.completed_files]
    
    def parse_filename(self, filename: str) -> Tuple[str, str]:
        """解析文件名获取章节号和标题"""
        # 匹配: chapter_01_1.2.1.3.1.1 标题.txt
        pattern = r'chapter_(\d+)_(.+?)\s+(.+?)\.txt'
        match = re.match(pattern, filename)
        if match:
            chapter_num = match.group(1)
            section_id = match.group(2)
            title = match.group(3)
            return chapter_num, f"{section_id} {title}"
        return "0", filename.replace('.txt', '')
    
    async def call_qwen_coder(self, prompt: str) -> str:
        """调用Qwen coder模型"""
        payload = {
            "model": "qwen-plus",  # 使用coder模型
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
                "max_tokens": 1500
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['output']['text'].strip()
                    else:
                        error_text = await response.text()
                        logger.error(f"API错误: {response.status}")
                        return ""
            except Exception as e:
                logger.error(f"API调用异常: {str(e)}")
                return ""
    
    def create_professional_svg_template(self, title: str, content_preview: str) -> str:
        """创建专业的PPT风格SVG模板"""
        # 截取合适长度的文本
        display_title = title[:60] + "..." if len(title) > 60 else title
        display_content = content_preview[:300] + "..." if len(content_preview) > 300 else content_preview
        
        # 专业配色方案
        colors = {
            'primary': '#2563eb',      # 蓝色主色
            'secondary': '#60a5fa',    # 浅蓝色
            'accent': '#1e40af',       # 深蓝色
            'background': '#f8fafc',   # 浅灰色背景
            'text': '#1e293b',         # 深灰色文字
            'light_text': '#64748b'    # 浅灰色文字
        }
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <!-- 背景渐变 -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{colors['background']}"/>
      <stop offset="100%" stop-color="#e2e8f0"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bgGradient)"/>
  
  <!-- 装饰性几何图形 -->
  <circle cx="1800" cy="150" r="80" fill="{colors['secondary']}" opacity="0.1"/>
  <circle cx="100" cy="950" r="60" fill="{colors['primary']}" opacity="0.1"/>
  <polygon points="1850,900 1880,950 1820,950" fill="{colors['accent']}" opacity="0.2"/>
  
  <!-- 主标题容器 -->
  <rect x="120" y="120" width="1680" height="160" rx="20" fill="white" stroke="{colors['primary']}" stroke-width="3"/>
  <rect x="120" y="120" width="20" height="160" fill="{colors['primary']}"/>
  
  <!-- 主标题 -->
  <text x="160" y="220" font-family="Arial, Helvetica, sans-serif" font-size="48" font-weight="bold" fill="{colors['text']}">
    {display_title}
  </text>
  
  <!-- 内容区域 -->
  <rect x="120" y="320" width="1680" height="600" rx="15" fill="white" stroke="#e2e8f0" stroke-width="2"/>
  
  <!-- 内容文本 -->
  <text x="160" y="380" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="{colors['text']}">
    {display_content}
  </text>
  
  <!-- 底部信息栏 -->
  <rect x="120" y="950" width="1680" height="60" rx="10" fill="{colors['primary']}" opacity="0.9"/>
  <text x="160" y="990" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="white">
    技术文档可视化展示
  </text>
  
  <!-- 装饰图标 -->
  <g transform="translate(1700, 960)">
    <circle cx="0" cy="0" r="15" fill="white" opacity="0.3"/>
    <circle cx="30" cy="0" r="12" fill="white" opacity="0.2"/>
    <circle cx="60" cy="0" r="10" fill="white" opacity="0.1"/>
  </g>
</svg>'''
        
        return svg
    
    async def generate_chapter_svg(self, filename: str, semaphore: asyncio.Semaphore) -> bool:
        """为单个章节生成SVG"""
        async with semaphore:
            try:
                chapter_num, title = self.parse_filename(filename)
                
                # 读取文件内容
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"处理章节 {chapter_num}: {title}")
                
                # 尝试使用Qwen coder生成专业SVG
                prompt = f"""请为以下技术内容创建一个专业的PPT风格SVG图表：

标题: {title}
内容要点: {content[:800]}

要求:
1. 标准SVG格式，尺寸1920x1080
2. 专业的商务配色方案
3. 包含标题区域和内容展示区
4. 添加适当的装饰元素
5. 文字清晰易读
6. 直接返回SVG代码，无需解释

请生成完整的SVG代码。"""

                svg_code = await self.call_qwen_coder(prompt)
                
                # 如果API失败，使用模板
                if not svg_code or '<svg' not in svg_code.lower():
                    logger.warning(f"API生成失败，使用模板: {filename}")
                    svg_code = self.create_professional_svg_template(title, content[:500])
                else:
                    # 清理API返回的代码
                    svg_code = self.cleanup_svg_response(svg_code)
                
                # 保存SVG文件
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:40]
                svg_filename = f"slide_{chapter_num.zfill(3)}_{safe_title}.svg"
                svg_path = os.path.join(self.output_dir, svg_filename)
                
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_code)
                
                # 更新进度
                self.completed_files.add(filename)
                self.save_progress()
                
                logger.info(f"✓ 完成: {svg_filename}")
                return True
                
            except Exception as e:
                logger.error(f"✗ 失败 {filename}: {str(e)}")
                return False
    
    def cleanup_svg_response(self, svg_code: str) -> str:
        """清理API返回的SVG代码"""
        # 移除代码块标记
        svg_code = svg_code.replace('```xml', '').replace('```svg', '').replace('```', '')
        svg_code = svg_code.strip()
        
        # 确保有正确的SVG标签
        if not svg_code.startswith('<?xml') and not svg_code.startswith('<svg'):
            svg_code = f'<?xml version="1.0" encoding="UTF-8"?>\n{svg_code}'
        
        if not svg_code.startswith('<svg'):
            svg_code = f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n{svg_code}\n</svg>'
            
        return svg_code
    
    async def process_all_chapters(self, concurrent_limit: int = 3):
        """批量处理所有章节"""
        files_to_process = self.get_chapter_files()
        
        if not files_to_process:
            logger.info("所有文件已处理完成!")
            return
        
        logger.info(f"开始处理 {len(files_to_process)} 个文件...")
        
        semaphore = asyncio.Semaphore(concurrent_limit)
        tasks = [self.generate_chapter_svg(filename, semaphore) for filename in files_to_process]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results if r is True)
        fail_count = len(results) - success_count
        
        logger.info(f"\n处理完成!")
        logger.info(f"成功: {success_count}")
        logger.info(f"失败: {fail_count}")
        logger.info(f"输出目录: {os.path.abspath(self.output_dir)}")

async def main():
    """主函数"""
    try:
        generator = SimpleSVGGenerator()
        await generator.process_all_chapters(concurrent_limit=3)
    except KeyboardInterrupt:
        logger.info("\n用户中断处理")
    except Exception as e:
        logger.error(f"程序错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())