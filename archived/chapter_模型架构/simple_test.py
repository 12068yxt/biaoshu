#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from concurrent_expand import ConcurrentDocumentExpander

# 测试标题解析
expander = ConcurrentDocumentExpander()

# 读取文档
with open("模型架构.md", "r", encoding="utf-8") as f:
    content = f.read()

print("=== 标题解析测试 ===")

# 测试五级标题
fifth_titles = expander.extract_all_fifth_level_titles(content)
print(f"五级标题数量: {len(fifth_titles)}")
for i, title in enumerate(fifth_titles[:3], 1):
    print(f"  {i}. {title}")

# 测试六级标题
sixth_titles = expander.extract_all_sixth_level_titles(content)
print(f"\n六级标题数量: {len(sixth_titles)}")
for i, title in enumerate(sixth_titles[:5], 1):
    print(f"  {i}. {title}")

print(f"\n总计: {len(fifth_titles) + len(sixth_titles)} 个标题")