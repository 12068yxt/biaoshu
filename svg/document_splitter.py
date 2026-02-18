#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档拆分模块

职责：
- 解析 .docx 文档所有段落
- 识别 Heading 1-5 样式（支持英文/中文多种命名格式）
- 维护层级路径栈（Heading 1-4 构建 hierarchy_path）
- 遇到 Heading 5 时创建新章节，收集后续正文
- 返回 List[Section] 列表

拆分逻辑详细说明：
  1. 遍历文档所有段落
  2. 遇到 Heading 1-4：更新层级栈，清除更低级别标题
  3. 遇到 Heading 5：
     a. 保存当前章节（如果存在）
     b. 以 Heading 1-4 栈构建 hierarchy_path（用">"连接）
     c. 创建新章节，标题=该段落文本
  4. 非标题段落：若有当前章节，追加到 content 列表
  5. 文档末尾：保存最后一个章节
"""

import os
import re
from typing import Dict, List, Optional

from docx import Document

from models import Section


class DocumentSplitter:
    """
    Word文档按 Heading 5 拆分器

    支持多种标题样式命名格式：
    - "Heading 1" ~ "Heading 5"（英文标准）
    - "Heading1" ~ "Heading5"（无空格）
    - "标题 1" ~ "标题 5"（中文Word）
    - "标题1" ~ "标题5"（中文无空格）

    Attributes:
        docx_path: Word文档的绝对或相对路径
    """

    def __init__(self, docx_path: str) -> None:
        """
        Args:
            docx_path: Word文档路径

        Raises:
            FileNotFoundError: 文档不存在
        """
        self.docx_path: str = docx_path

    # ------------------------------------------------------------------
    # 样式识别辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _get_style_name(paragraph) -> str:
        """
        安全获取段落样式名称

        Args:
            paragraph: python-docx 段落对象

        Returns:
            样式名称字符串，无样式时返回空字符串
        """
        return paragraph.style.name if paragraph.style else ""

    @staticmethod
    def _heading_level(style_name: str) -> int:
        """
        判断样式是否为 Heading 1-5，返回级别数字

        支持格式：
        - "Heading 1" / "Heading1"（英文）
        - "标题 1" / "标题1"（中文）
        - 大小写不敏感

        Args:
            style_name: 段落样式名称

        Returns:
            标题级别（1-5），非标题返回 0
        """
        if not style_name:
            return 0
        # 匹配：Heading 1~5 或 标题 1~5
        patterns = [
            r"^heading\s*([1-5])$",  # 英文（含无空格）
            r"^标题\s*([1-5])$",      # 中文（含无空格）
        ]
        normalized = style_name.strip().lower()
        for pattern in patterns:
            m = re.match(pattern, normalized)
            if m:
                return int(m.group(1))
        return 0

    # ------------------------------------------------------------------
    # 主拆分方法
    # ------------------------------------------------------------------

    def split_by_heading5(self) -> List[Section]:
        """
        按 Heading 5 拆分文档，返回 Section 列表

        Returns:
            Section 对象列表（按文档顺序，index 从 0 开始）

        Raises:
            FileNotFoundError: 文档文件不存在
            Exception: docx 解析错误（向上传播）
        """
        if not os.path.exists(self.docx_path):
            raise FileNotFoundError(f"Word文档不存在: {self.docx_path}")

        doc = Document(self.docx_path)

        sections: List[Section] = []
        # 当前正在收集的章节（None 表示尚未遇到 Heading 5）
        current: Optional[Dict] = None
        # 层级栈：{level(1-4): title_text}
        heading_stack: Dict[int, str] = {}

        for para in doc.paragraphs:
            style_name = self._get_style_name(para)
            text = para.text.strip()

            # 跳过空段落
            if not text:
                continue

            level = self._heading_level(style_name)

            if level > 0:
                # ---- 是标题段落 ----

                # 更新层级栈：设置当前级别，清除更低级别
                heading_stack[level] = text
                for lower in [k for k in heading_stack if k > level]:
                    del heading_stack[lower]

                if level == 5:
                    # Heading 5：保存当前章节，开始新章节
                    if current is not None:
                        sections.append(self._build_section(current, len(sections)))

                    # 构建 hierarchy_path（Heading 1-4，不含 Heading 5 自身）
                    hierarchy_parts = [
                        heading_stack[l]
                        for l in sorted(heading_stack)
                        if l < 5
                    ]
                    hierarchy_path = ">".join(hierarchy_parts)

                    # 开始新章节
                    current = {
                        "title": text,
                        "content": [],
                        "hierarchy_path": hierarchy_path,
                    }
                # else: Heading 1-4 只更新层级栈，不开启新章节

            else:
                # ---- 非标题段落（正文）----
                if current is not None:
                    current["content"].append(text)

        # 保存最后一个章节
        if current is not None:
            sections.append(self._build_section(current, len(sections)))

        return sections

    @staticmethod
    def _build_section(raw: Dict, index: int) -> Section:
        """
        从原始字典构建 Section 对象

        Args:
            raw: 包含 title / content(list) / hierarchy_path 的字典
            index: 章节序号（0-based）

        Returns:
            Section 实例
        """
        return Section(
            index=index,
            title=raw["title"],
            # 合并正文段落，\n 分隔，完整传递不截断
            content="\n".join(raw["content"]),
            hierarchy_path=raw["hierarchy_path"],
        )
