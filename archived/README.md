# biaoshu - 技术标书智能扩充系统

基于阿里云通义千问(Qwen-Plus)的AI驱动技术文档自动生成工具，专为提升技术标书撰写效率而设计。

## 🎯 项目简介

biaoshu是一个智能化的技术文档处理系统，能够自动识别文档结构、提取关键章节，并通过AI生成高质量的技术内容扩充。系统支持多种文档格式，具备并发处理能力，可大幅提升技术文档编写效率。

## 🚀 核心功能

- **智能章节识别**: 自动提取Markdown/TXT文档中的多级标题结构
- **AI内容生成**: 基于阿里云通义千问生成3000-4000字的专业技术内容
- **并发处理**: 支持最多3个并发API请求，显著提升处理速度
- **进度跟踪**: 实时保存处理进度，支持断点续传
- **双保存机制**: 同时生成主文件和独立章节文件
- **SVG图表生成**: 自动生成PPT兼容的技术图表

## 📁 项目结构

```
biaoshu/
├── chapter_1.2.1.3/          # 技术章节文件目录
├── svg/                      # SVG图表生成器
│   ├── ppt_svg_generator.py  # 核心生成脚本
│   ├── advanced_svg_config.json  # 增强配置文件
│   └── README.md             # SVG生成器使用说明
├── tmp/                      # 脚本文件集中管理目录
├── sample/                   # 示例文件和测试数据
├── templates/                # 配置模板目录
├── generated_svgs/           # 生成的SVG文件输出目录
├── debug_svgs/               # 调试用SVG文件目录
└── README.md                 # 项目主说明文件
```

## ⚙️ 环境配置

### 必需依赖
```bash
# Python 3.8+
pip install aiohttp>=3.8
```

### API密钥配置
```bash
# 已配置为全局环境变量
export ALIYUN_API_KEY="sk-19278db0ad4b436d9bf381e0c04c56dc"
```

## 🛠️ 使用方法

### 1. 文档内容扩充
```bash
# 进入项目目录
cd /home/xiaoting/biaoshu

# 运行内容扩充程序
python tmp/concurrent_expand.py
```

### 2. SVG图表生成
```bash
# 调试模式（预览提示词）
python svg/ppt_svg_generator.py --mode debug

# 批量生成图表
python svg/ppt_svg_generator.py --mode batch

# 列出可用图表模板
python svg/ppt_svg_generator.py --list-prompts
```

### 3. 快速开始脚本
```bash
# 运行SVG生成
cd svg && ./run_svg_generation.sh
```

## 📊 系统特性

### 并发处理
- 最多支持3个并发API请求
- 指数退避重试机制
- 超时时间120秒以上

### 文件管理
- 自动备份原始文件
- 智能文件命名规则
- 实时进度保存

### 质量保证
- 内容专业性强，逻辑严谨
- 支持多种技术文档格式
- 可配置的内容生成参数

## 🔧 配置文件

主要配置文件位于 `tmp/config.json`，包含：
- API配置参数
- 文档处理设置
- 并发控制选项
- 文件路径配置

## 📈 性能指标

- **处理速度**: 3并发请求显著提升效率
- **内容质量**: 3000-4000字专业技术内容
- **成功率**: 具备完善的错误处理和重试机制
- **稳定性**: 支持长时间运行和断点续传

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目仅供学习和研究使用。

---
*Powered by 阿里云通义千问*