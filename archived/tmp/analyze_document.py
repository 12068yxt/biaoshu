#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取工作原理.md中的六级子标题
"""

import re

def extract_sixth_level_titles():
    try:
        with open("工作原理.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        lines = content.split('\n')
        sixth_level_titles = []
        
        # 匹配六级标题格式 (### 1.2.1.3.1.1 这样的格式)
        sixth_level_pattern = r'^###\s+(\d+(?:\.\d+)*)\s+(.+)$'
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            match = re.match(sixth_level_pattern, line)
            if match:
                number = match.group(1)  # 1.2.1.3.1.1
                title_text = match.group(2)  # 标题文字部分
                full_title = f"{number} {title_text}"
                
                sixth_level_titles.append({
                    'line_number': line_num,
                    'number': number,
                    'text': title_text,
                    'full_title': full_title
                })
        
        print(f"找到 {len(sixth_level_titles)} 个六级子标题:")
        print("="*60)
        
        for i, title in enumerate(sixth_level_titles, 1):
            print(f"{i:2d}. {title['full_title']}")
            
        # 保存到文件
        with open("sixth_level_titles.txt", "w", encoding="utf-8") as f:
            for title in sixth_level_titles:
                f.write(f"{title['full_title']}\n")
        
        print(f"\n已将六级标题保存到 sixth_level_titles.txt 文件中")
        return sixth_level_titles
        
    except FileNotFoundError:
        print("未找到工作原理.md文件")
        return []
    except Exception as e:
        print(f"提取标题时出错: {str(e)}")
        return []

if __name__ == "__main__":
    titles = extract_sixth_level_titles()