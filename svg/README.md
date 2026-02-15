# PPT兼容SVG技术图表生成器

这是一个专门为技术文档生成PPT兼容的黑白线框风格SVG图表的工具。

## 功能特点

- ✅ 自动生成PPT兼容的1920x1080尺寸SVG图表
- ✅ 支持多种图表类型：流程图、架构图、数据流图、网络拓扑图
- ✅ 黑白线框风格，专业简洁
- ✅ 自动识别内容类型并选择合适的图表模板
- ✅ 支持批量处理章节文件
- ✅ 提供调试模式，可预览和调整提示词
- ✅ 进度跟踪和断点续传功能

## 安装依赖

```bash
pip install aiohttp
```

## 环境配置

设置阿里云API密钥：
```bash
export ALIYUN_API_KEY="your-api-key-here"
```

## 使用方法

### 1. 查看可用的图表类型和提示词

```bash
python ppt_svg_generator.py --list-prompts
```

### 2. 调试模式 - 预览提示词

```bash
python ppt_svg_generator.py --mode debug
```

这会处理前3个章节文件，只显示生成的提示词而不调用API。

### 3. 测试单个提示词

```bash
python ppt_svg_generator.py --mode test \
  --diagram-type flowchart \
  --title "自注意力机制流程" \
  --content "自注意力机制包括查询、键、值向量的计算，相似度计算，softmax归一化，加权求和等步骤..."
```

### 4. 批量生成SVG图表

```bash
python ppt_svg_generator.py --mode batch
```

### 5. 指定不同的章节目录

```bash
python ppt_svg_generator.py --mode batch --chapter-dir "../other_chapters"
```

### 6. 调整并发数量

```bash
python ppt_svg_generator.py --mode batch --max-concurrent 5
```

## 图表类型说明

### 流程图 (flowchart)
适合展示算法步骤、处理流程、工作流等线性过程。

### 架构图 (architecture)
适合展示系统组件、模块结构、软件架构等层次化关系。

### 数据流图 (data_flow)
适合展示数据流向、信息处理、数据管道等数据相关的流程。

### 网络拓扑图 (network_topology)
适合展示网络设备连接、通信结构等网络相关图表。

## 输出文件

生成的SVG文件保存在 `../generated_svgs/` 目录下，文件命名格式为：
`chapter_{编号}_{标题}.svg`

## 配置文件

- `svg_config.json` - 基础配置文件
- `advanced_svg_config.json` - 增强配置文件（包含调试选项）

## 进度跟踪

程序会自动保存处理进度到 `../svg_generation_progress.json`，支持断点续传。

## 日志文件

详细的运行日志保存在 `svg_generation.log` 文件中。

## 调试技巧

1. **使用调试模式**：先用 `--mode debug` 查看生成的提示词是否合适
2. **手动测试提示词**：使用 `--mode test` 测试特定的提示词效果
3. **调整配置文件**：修改 `advanced_svg_config.json` 中的提示词模板
4. **查看日志**：检查 `svg_generation.log` 了解详细的执行过程

## 常见问题

### Q: API调用失败怎么办？
A: 检查环境变量 `ALIYUN_API_KEY` 是否正确设置，查看日志文件了解具体错误。

### Q: 生成的SVG格式不正确？
A: 可能是API返回的内容有问题，尝试在调试模式下查看提示词，调整提示词内容。

### Q: 如何添加新的图表类型？
A: 在配置文件的 `prompts` 部分添加新的图表类型配置。

### Q: 如何修改SVG样式？
A: 修改配置文件中的 `default_style` 部分，或在提示词中明确指定样式要求。