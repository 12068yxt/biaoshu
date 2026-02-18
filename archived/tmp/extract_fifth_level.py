#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取text.md文件中的五级标题
"""

import re
from typing import List

def extract_fifth_level_titles_from_text_md() -> List[str]:
    """从text.md文件中提取五级标题"""
    try:
        with open("text.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("错误: 未找到 text.md 文件")
        return []
    
    # 匹配五级标题格式 (如 1.2.5.1 这样的数字格式)
    # 这些标题在文件中是以纯数字形式出现的，没有Markdown标记
    pattern = r'^(\d+\.\d+\.\d+\.\d+)\s+(.+)$'
    titles = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            number = match.group(1)
            title_text = match.group(2)
            # 移除可能的页数信息 (如 (15页))
            title_text = re.sub(r'\(\d+页\)$', '', title_text).strip()
            full_title = f"{number} {title_text}"
            titles.append(full_title)
    
    return titles

def main():
    """主函数"""
    print("正在提取text.md中的五级标题...")
    
    titles = extract_fifth_level_titles_from_text_md()
    
    if titles:
        print(f"\n找到 {len(titles)} 个五级标题:")
        print("-" * 50)
        for i, title in enumerate(titles, 1):
            print(f"{i:2d}. {title}")
        
        # 保存到文件
        with open("extracted_fifth_level_titles.txt", "w", encoding="utf-8") as f:
            for title in titles:
                f.write(f"{title}\n")
        print(f"\n✓ 已将标题保存到 extracted_fifth_level_titles.txt")
    else:
        print("未找到任何五级标题")

if __name__ == "__main__":
    main()