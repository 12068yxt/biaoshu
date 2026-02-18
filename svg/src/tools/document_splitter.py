#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档拆分工具

Rule 4: 失败优雅降级原则
单节点失败不中断整体流程
"""

import os
import re
from typing import List, Optional, Dict
from docx import Document

from ..agents.state import Section
from ..utils import register_tool


@register_tool("document_splitter")
class DocumentSplitter:
    """
    文档拆分类

    负责：
    1. 解析 docx 文档
    2. 识别 Heading 5 标题
    3. 构建层级路径（Heading 1-4）
    4. 收集章节内容

    Attributes:
        docx_path: Word 文档路径
    """

    def __init__(self, docx_path: str):
        """
        初始化文档拆分器

        Args:
            docx_path: Word 文档路径
        """
        self.docx_path = docx_path

    def _get_paragraph_style(self, paragraph) -> Optional[str]:
        """
        获取段落的样式名称

        Args:
            paragraph: docx 段落对象

        Returns:
            样式名称（如"Heading 1"），如果不是标题则返回 None
        """
        style_name = paragraph.style.name if paragraph.style else None
        return style_name

    def _is_heading(self, style_name: Optional[str], level: int) -> bool:
        """
        检查样式是否为指定级别的标题

        Args:
            style_name: 样式名称
            level: 标题级别（1-5）

        Returns:
            是否匹配
        """
        if not style_name:
            return False
        # 支持多种命名格式："Heading 1", "Heading1", "标题 1"等
        patterns = [
            f"^Heading {level}$",
            f"^Heading{level}$",
            f"^标题 {level}$",
            f"^标题{level}$",
        ]
        return any(re.match(pattern, style_name, re.IGNORECASE) for pattern in patterns)

    def _is_any_heading(self, style_name: Optional[str]) -> bool:
        """
        检查样式是否为任意级别的标题（Heading 1-5）

        Args:
            style_name: 样式名称

        Returns:
            是否为标题样式
        """
        if not style_name:
            return False
        patterns = [
            r"^Heading [1-5]$",
            r"^Heading[1-5]$",
            r"^标题 [1-5]$",
            r"^标题[1-5]$",
        ]
        return any(re.match(pattern, style_name, re.IGNORECASE) for pattern in patterns)

    def split_by_heading5(self) -> List[Section]:
        """
        按 Heading 5 拆分文档

        拆分逻辑：
        1. 遍历文档所有段落
        2. 遇到"Heading 5"时，创建新章节，该标题作为章节标题
        3. 收集后续段落内容（非 Heading 样式），作为章节正文
        4. 遇到下一个"Heading 1-5"时，当前章节结束
        5. 层级路径：拼接当前章节所在的上级标题（Heading 1-4），用">"连接

        Returns:
            Section 对象列表

        Raises:
            FileNotFoundError: 文档不存在
            Exception: 文档解析错误
        """
        if not os.path.exists(self.docx_path):
            raise FileNotFoundError(f"文档不存在: {self.docx_path}")

        # 加载文档
        doc = Document(self.docx_path)

        sections: List[Section] = []
        current_section: Optional[Dict] = None

        # 层级路径追踪
        heading_stack: Dict[int, str] = {}  # {level: title}

        for paragraph in doc.paragraphs:
            style_name = self._get_paragraph_style(paragraph)
            text = paragraph.text.strip()

            if not text:
                continue

            # 检查是否为 Heading 1-5
            is_heading = False
            heading_level = 0

            for level in range(1, 6):
                if self._is_heading(style_name, level):
                    is_heading = True
                    heading_level = level
                    break

            if is_heading:
                # 更新层级路径
                heading_stack[heading_level] = text
                # 清除更低级别的标题
                for l in list(heading_stack.keys()):
                    if l > heading_level:
                        del heading_stack[l]

                # 如果是 Heading 5，创建新章节
                if heading_level == 5:
                    # 先保存当前章节（如果存在）
                    if current_section:
                        sections.append(Section(
                            index=len(sections),
                            title=current_section['title'],
                            content='\n'.join(current_section['content']),
                            hierarchy_path=current_section['hierarchy_path']
                        ))

                    # 构建层级路径（Heading 1-4）
                    hierarchy_parts = []
                    for l in range(1, 5):
                        if l in heading_stack:
                            hierarchy_parts.append(heading_stack[l])
                    hierarchy_path = '>'.join(hierarchy_parts) if hierarchy_parts else ""

                    # 创建新章节
                    current_section = {
                        'title': text,
                        'content': [],
                        'hierarchy_path': hierarchy_path
                    }
            else:
                # 非标题段落，添加到当前章节内容
                if current_section is not None:
                    current_section['content'].append(text)

        # 保存最后一个章节
        if current_section:
            sections.append(Section(
                index=len(sections),
                title=current_section['title'],
                content='\n'.join(current_section['content']),
                hierarchy_path=current_section['hierarchy_path']
            ))

        return sections
