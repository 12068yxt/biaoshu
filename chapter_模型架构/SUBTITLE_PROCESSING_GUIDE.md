# 小标题处理功能使用指南

## 功能概述

本项目新增了小标题解析和内容生成功能，可以处理文档中的深层级标题结构，包括：

- **五级标题**: `## ▼ 1.2.2.11. 长文本处理与上下文扩展技术`
- **六级标题**: `### 1.2.2.11.1. 滑动窗口注意力机制`
- **七级标题**: 更深层级的小标题（可根据需要扩展）

## 文件结构

```
chapter_模型架构/
├── concurrent_expand.py          # 主程序，包含标题解析功能
├── subtitle_processor.py         # 专门的小标题处理器
├── config.json                  # 配置文件
├── 模型架构.md                  # 源文档
├── test_subtitle_extraction.py  # 小标题解析测试
├── demo_subtitle_processing.py  # 功能演示脚本
└── SUBTITLE_PROCESSING_GUIDE.md # 本使用指南
```

## 核心功能

### 1. 标题解析功能

支持多种标题格式的自动识别和提取：

```python
from concurrent_expand import ConcurrentDocumentExpander

expander = ConcurrentDocumentExpander()

# 提取五级标题
fifth_titles = expander.extract_all_fifth_level_titles(content)

# 提取六级标题  
sixth_titles = expander.extract_all_sixth_level_titles(content)

# 根据配置提取指定级别标题
titles = expander.extract_all_titles(content, level=6)
```

### 2. 内容生成功能

```python
# 生成单个章节内容
result = await expander.generate_section_content(session, title, index, total)

# 批量处理整个文档
await expander.process_document()
```

### 3. 文件保存功能

- **主文件追加**: 内容自动追加到 `_expanded.md` 文件
- **独立文件保存**: 每个章节保存为单独的 `chapter_{编号}._{标题}.md` 文件

## 使用方法

### 1. 环境准备

```bash
# 设置API密钥
export ALIYUN_API_KEY="your_api_key_here"

# 安装依赖
pip install aiohttp
```

### 2. 配置设置

编辑 `config.json` 文件：

```json
{
    "api_settings": {
        "temperature": 0.7,
        "max_tokens": 3500,
        "timeout": 120
    },
    "title_settings": {
        "title_level": 6,
        "enable_subtitles": true
    },
    "document_settings": {
        "source_file": "模型架构.md",
        "supported_extensions": [".md", ".txt"],
        "backup_enabled": true
    }
}
```

### 3. 运行处理

```bash
# 运行主程序处理文档
python concurrent_expand.py

# 运行小标题专门处理器
python subtitle_processor.py

# 查看功能演示
python demo_subtitle_processing.py

# 测试标题解析功能
python test_subtitle_extraction.py
```

## 标题格式支持

### 支持的标题格式

1. **五级标题格式**:
   ```
   ## ▼ 1.2.2.11. 长文本处理与上下文扩展技术
   ## 1.2.2.12. 模型安全性与可靠性设计
   ```

2. **六级标题格式**:
   ```
   ### 1.2.2.11.1. 滑动窗口注意力机制
   ### 1.2.2.11.2. 分层位置编码设计
   ```

3. **七级标题格式**（可扩展）:
   ```
   #### 1.2.2.11.1.1. 详细技术说明
   1.2.2.11.1.1.1 具体实现细节
   ```

### 标题解析特点

- 自动识别带特殊符号（如▼）的标题
- 支持去除页数标注等附加信息
- 智能处理不同层级的标题结构
- 支持Markdown和纯文本格式

## 输出文件格式

### 主输出文件
`模型架构_expanded.md` - 包含所有生成内容的完整文档

### 独立章节文件
`chapter_1.2.2.11.1._滑动窗口注意力机制.md` - 单独的章节文件

### 文件命名规则
- 使用编号和标题组合命名
- 自动清理特殊字符
- 保持标题的可读性

## 高级功能

### 1. 断点续传
- 自动保存处理进度
- 支持中断后继续处理
- 避免重复生成已处理内容

### 2. 并发处理
- 支持3个并发API请求
- 智能的任务队列管理
- 高效的资源利用

### 3. 错误处理
- 指数退避重试机制
- 详细的错误日志记录
- 失败任务的统计分析

## 最佳实践

### 1. 文档准备
- 确保文档格式规范统一
- 标题层级结构清晰
- 避免特殊字符干扰解析

### 2. 配置优化
- 根据文档特点调整标题级别
- 合理设置API参数
- 启用适当的备份功能

### 3. 运行监控
- 定期检查处理进度
- 关注API调用成功率
- 及时处理失败的任务

## 故障排除

### 常见问题

1. **标题无法识别**
   - 检查文档格式是否符合预期
   - 验证正则表达式匹配规则
   - 运行测试脚本验证解析功能

2. **API调用失败**
   - 确认API密钥设置正确
   - 检查网络连接状态
   - 查看错误日志详细信息

3. **文件保存问题**
   - 确认目录权限设置
   - 检查磁盘空间充足
   - 验证文件名合法性

### 调试方法

```bash
# 运行测试脚本
python test_subtitle_extraction.py

# 查看详细日志
python concurrent_expand.py 2>&1 | tee processing.log

# 使用演示脚本验证功能
python demo_subtitle_processing.py
```

## 扩展开发

### 添加新的标题级别

```python
def extract_all_eighth_level_titles(self, content: str) -> List[str]:
    """提取八级标题"""
    # 实现八级标题解析逻辑
    pass

# 在extract_all_titles方法中添加支持
elif level == 8:
    return self.extract_all_eighth_level_titles(content)
```

### 自定义提示词模板

```python
def create_custom_prompt(self, title: str, template_type: str = "technical") -> str:
    """创建自定义提示词"""
    templates = {
        "technical": "技术文档模板...",
        "academic": "学术论文模板...",
        "business": "商业报告模板..."
    }
    return templates.get(template_type, templates["technical"]).format(title=title)
```

## 版本历史

- **v1.0**: 基础标题解析和内容生成功能
- **v1.1**: 新增小标题处理专门功能
- **v1.2**: 优化并发处理和错误处理机制

---
如需更多帮助，请参考相关测试脚本或联系技术支持。