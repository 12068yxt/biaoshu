# PPT风格SVG生成器使用说明

## 🎯 功能简介

这是一个专门为技术文档章节生成PPT风格SVG图表的自动化工具，可以：

- 🎨 为每个章节自动生成专业的可视化SVG图表
- 📊 创建完整的PowerPoint演示文稿
- 🌐 生成可在浏览器中演示的HTML版本
- ⚡ 支持并发处理，提高生成效率
- 🔧 高度可配置，支持自定义样式

## 📁 文件结构

```
biaoshu/
├── generate_ppt_svgs.py        # 完整版生成器（高级功能）
├── simple_svg_generator.py     # 简化版生成器（推荐使用）
├── ppt_importer.py            # PPT导入工具
├── run_ppt_generation.sh      # 一键执行脚本
├── ppt_config.json            # 配置文件
├── PPT_SVG_GENERATOR_README.md # 本说明文档
├── generated_svgs/            # 生成的SVG文件目录
├── ppt_presentations/         # 生成的PPT文件目录
└── chapter_*.txt              # 待处理的章节文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 设置阿里云API密钥（必需）
export ALIYUN_API_KEY="your-api-key-here"

# 安装必要的Python包
pip3 install aiohttp python-pptx cairosvg
```

### 2. 一键生成

```bash
# 给脚本添加执行权限
chmod +x run_ppt_generation.sh

# 运行一键生成脚本
./run_ppt_generation.sh
```

### 3. 分步执行

```bash
# 步骤1: 生成SVG文件
python3 simple_svg_generator.py

# 步骤2: 导入到PPT
python3 ppt_importer.py
```

## ⚙️ 配置说明

### 主要配置项 (ppt_config.json)

```json
{
  "api_settings": {
    "model": "qwen-plus",        // 使用的模型
    "temperature": 0.7,          // 创造性参数
    "max_tokens": 1500,          // 最大输出长度
    "timeout": 120               // API超时时间
  },
  "processing_settings": {
    "concurrent_limit": 3,       // 并发处理数量
    "content_preview_length": 800 // 内容预览长度
  }
}
```

## 🎨 自定义样式

### 修改颜色方案

在 `ppt_config.json` 中调整配色：

```json
"color_scheme": {
  "primary": "#2563eb",     // 主色调
  "secondary": "#60a5fa",   // 辅助色
  "accent": "#1e40af",      // 强调色
  "text": "#1e293b",        // 文字颜色
  "light_text": "#64748b"   // 浅色文字
}
```

### 调整字体大小

```json
"svg_template": {
  "title_font_size": 48,     // 标题字体大小
  "content_font_size": 28    // 内容字体大小
}
```

## 📊 输出文件说明

### SVG文件特点
- ✅ 1920×1080分辨率，完美适配PPT
- ✅ 专业商务配色方案
- ✅ 响应式布局设计
- ✅ 包含章节标题和内容预览
- ✅ 可直接在浏览器中查看

### PPT文件特点
- ✅ 16:9宽屏比例
- ✅ 每张幻灯片对应一个章节
- ✅ 自动添加页脚信息
- ✅ 支持PowerPoint原生编辑

### HTML演示文稿特点
- ✅ 全屏浏览器演示
- ✅ 键盘控制（左右箭头键）
- ✅ 显示幻灯片进度
- ✅ 无需额外软件即可演示

## 🔧 高级用法

### 断点续传
程序会自动记录处理进度，中断后可直接重新运行继续处理。

### 单独处理特定文件
修改 `simple_svg_generator.py` 中的文件筛选逻辑：

```python
def get_chapter_files(self) -> List[str]:
    # 只处理特定章节
    files = [f for f in os.listdir('.') if f.startswith('chapter_01')]
    return [f for f in files if f not in self.completed_files]
```

### 自定义SVG模板
修改 `create_professional_svg_template` 方法来自定义图表样式。

## 🐛 常见问题

### Q: API调用失败怎么办？
A: 检查API密钥是否正确设置，网络连接是否正常

### Q: 生成的SVG显示不正常？
A: 确保使用现代浏览器查看，或尝试转换为PNG格式

### Q: PPT文件无法打开？
A: 确保已安装Microsoft PowerPoint或兼容软件

### Q: 如何调整并发数量？
A: 修改配置文件中的 `concurrent_limit` 参数

## 📈 性能优化

### 推荐配置
- CPU: 4核以上
- 内存: 8GB以上
- 网络: 稳定的互联网连接
- 并发数: 3-5个（根据API限制调整）

### 处理时间估算
- 单个文件: 10-30秒
- 72个文件: 10-15分钟（3并发）
- 具体时间取决于API响应速度

## 🤝 技术支持

如遇到问题，请检查：
1. 环境变量是否正确设置
2. 依赖包是否完整安装
3. 配置文件格式是否正确
4. 查看生成的日志文件

## 📝 版本历史

- v1.0: 基础功能实现
- v1.1: 添加HTML演示功能
- v1.2: 优化并发处理和错误处理
- v1.3: 添加配置文件支持

---
**注意**: 本工具需要有效的阿里云API密钥才能正常使用Qwen模型生成SVG内容。