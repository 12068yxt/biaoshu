#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能绘图工具

Rule 4: 失败优雅降级原则
- LLM 调用失败自动重试（指数退避，最多 3 次）
- 响应格式错误生成备用内容（fallback）
"""

import os
import re
import time
from typing import Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..agents.state import Section, SVGResult
from ..config import ConfigManager
from ..utils import register_tool


@register_tool("smart_drawer")
class SmartDrawer:
    """
    智能绘图类

    负责：
    1. 提示词组装（调用 ConfigManager）
    2. LLM 调用（带重试机制）
    3. SVG 验证和修复
    4. 失败回退（生成极简备用 SVG）

    Attributes:
        config_manager: 配置管理器实例
        llm: LangChain LLM 实例
        retry_times: 重试次数
    """

    def __init__(self, config_manager: ConfigManager):
        """
        初始化智能绘图器

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.llm_config = config_manager.get_llm_config()
        self.retry_times = self.llm_config.get('retry_times', 2)

        # 初始化 LLM
        api_key = self.llm_config.get('api_key')
        base_url = self.llm_config.get('base_url')
        
        # OpenRouter 需要额外的 headers
        default_headers = None
        if 'openrouter.ai' in (base_url or ''):
            default_headers = {
                "HTTP-Referer": "https://localhost",
                "X-Title": "SVG Workflow"
            }
        
        self.llm = ChatOpenAI(
            model=self.llm_config.get('model', 'gpt-4o'),
            temperature=self.llm_config.get('temperature', 0.3),
            max_tokens=self.llm_config.get('max_tokens', 4000),
            base_url=base_url,
            api_key=api_key,
            default_headers=default_headers,
        )

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用 LLM 生成 SVG

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            LLM 生成的 SVG 代码

        Raises:
            Exception: LLM 调用失败
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content

    def _extract_svg(self, content: str) -> Optional[str]:
        """
        从 LLM 响应中提取 SVG 代码

        Args:
            content: LLM 原始响应

        Returns:
            提取的 SVG 代码，如果没有找到则返回 None
        """
        # 查找 <svg> 标签
        svg_match = re.search(r'<svg[^>]*>.*?</svg>', content, re.DOTALL | re.IGNORECASE)
        if svg_match:
            svg_content = svg_match.group(0)

            # 检查是否有 XML 声明
            if not svg_content.startswith('<?xml'):
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

            return svg_content

        return None

    def _validate_svg(self, svg_content: str) -> Tuple[bool, str]:
        """
        验证 SVG 代码的完整性和正确性

        验证项：
        1. 包含 <svg> 标签
        2. 包含 xmlns 命名空间
        3. 包含 viewBox 属性
        4. 标签正确闭合

        Args:
            svg_content: SVG 代码

        Returns:
            (是否有效, 错误信息) 元组
        """
        # 检查 <svg> 标签
        if '<svg' not in svg_content.lower():
            return False, "缺少<svg>标签"

        # 检查 xmlns
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            return False, "缺少xmlns命名空间"

        # 检查 viewBox
        if 'viewBox' not in svg_content:
            return False, "缺少viewBox属性"

        # 检查标签闭合
        svg_open_count = len(re.findall(r'<svg[^>]*>', svg_content, re.IGNORECASE))
        svg_close_count = len(re.findall(r'</svg>', svg_content, re.IGNORECASE))
        if svg_open_count != svg_close_count:
            return False, "<svg>标签未正确闭合"

        return True, ""

    def _fix_svg(self, svg_content: str) -> str:
        """
        自动修复 SVG 代码中的常见问题

        修复项：
        1. 添加缺失的 xmlns
        2. 添加缺失的 viewBox
        3. 确保 XML 声明

        Args:
            svg_content: 原始 SVG 代码

        Returns:
            修复后的 SVG 代码
        """
        # 确保 XML 声明
        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        # 添加 xmlns（如果不存在）
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)

        # 添加 viewBox（如果不存在）
        if 'viewBox' not in svg_content:
            # 尝试提取 width 和 height
            width_match = re.search(r'width=["\'](\d+)["\']', svg_content)
            height_match = re.search(r'height=["\'](\d+)["\']', svg_content)

            if width_match and height_match:
                width = width_match.group(1)
                height = height_match.group(1)
                svg_content = svg_content.replace('<svg', f'<svg viewBox="0 0 {width} {height}"', 1)
            else:
                # 默认 viewBox
                svg_content = svg_content.replace('<svg', '<svg viewBox="0 0 800 600"', 1)

        return svg_content

    def _generate_fallback_svg(self, title: str) -> str:
        """
        生成极简备用 SVG

        当 LLM 调用失败时，生成一个简单的占位 SVG

        Args:
            title: 章节标题

        Returns:
            备用 SVG 代码
        """
        # 硬编码备用样式
        bg_color = '#FFFFFF'
        text_color = '#1A2B4C'
        primary_color = '#1E5FC5'

        # 截断标题（避免过长）
        display_title = title[:50] + "..." if len(title) > 50 else title

        fallback_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <rect width="800" height="600" fill="{bg_color}"/>
  <rect x="50" y="50" width="700" height="500" rx="10" fill="none" stroke="{primary_color}" stroke-width="2"/>
  <text x="400" y="280" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="{text_color}">
    {display_title}
  </text>
  <text x="400" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="{primary_color}">
    [SVG生成失败 - 备用图表]
  </text>
</svg>'''
        return fallback_svg

    def draw(
        self,
        section: Section,
        output_dir: str = "output/svgs"
    ) -> SVGResult:
        """
        为章节生成 SVG 图表

        流程：
        1. 组装提示词（调用 ConfigManager.render_prompts）
        2. 调用 LLM（带重试机制）
        3. 提取和验证 SVG
        4. 保存 SVG 文件
        5. 失败时生成备用 SVG

        Args:
            section: 章节对象
            output_dir: SVG 输出目录

        Returns:
            SVGResult 对象
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 准备输出路径
        safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', section.title)[:30]
        svg_filename = f"section_{section.index:03d}_{safe_title}.svg"
        svg_path = os.path.join(output_dir, svg_filename)

        # 渲染提示词
        system_prompt, user_prompt = self.config_manager.render_prompts(
            title=section.title,
            content=section.content,
            hierarchy_path=section.hierarchy_path
        )

        # 重试机制（指数退避）
        last_error = ""
        base_delay = self.llm_config.get('retry_base_delay', 1.0)

        for attempt in range(self.retry_times + 1):
            try:
                # 调用 LLM
                llm_response = self._call_llm(system_prompt, user_prompt)

                # 提取 SVG
                svg_content = self._extract_svg(llm_response)

                if svg_content is None:
                    last_error = "无法从LLM响应中提取SVG代码"
                    continue

                # 验证 SVG
                is_valid, error_msg = self._validate_svg(svg_content)

                if not is_valid:
                    # 尝试修复
                    svg_content = self._fix_svg(svg_content)
                    is_valid, error_msg = self._validate_svg(svg_content)

                    if not is_valid:
                        last_error = f"SVG验证失败: {error_msg}"
                        continue

                # 保存 SVG 文件
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)

                return SVGResult(
                    section_index=section.index,
                    section_title=section.title,
                    svg_content=svg_content,
                    svg_path=svg_path,
                    success=True
                )

            except Exception as e:
                last_error = str(e)
                if attempt < self.retry_times:
                    # 指数退避
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue

        # 所有重试失败，生成备用 SVG
        fallback_svg = self._generate_fallback_svg(section.title)

        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(fallback_svg)

        return SVGResult(
            section_index=section.index,
            section_title=section.title,
            svg_content=fallback_svg,
            svg_path=svg_path,
            success=False,
            error_message=f"LLM调用失败（重试{self.retry_times}次）: {last_error}"
        )
