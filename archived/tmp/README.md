# 大模型技术标书内容扩充工具

## 使用说明

### 1. 环境准备
```bash
# 安装必要的Python依赖
pip3 install aiohttp

# 设置阿里云API密钥环境变量
export ALIYUN_API_KEY="sk-19278db0ad4b436d9bf381e0c04c56dc"
```

### 2. 配置说明
- `config.json`: 主配置文件，包含API设置、文档配置和标题处理配置
- 源文档: 通过配置文件指定待扩充的目标文档

#### 文档文件配置
在 `config.json` 中通过 `document_settings` 配置文档路径：

```json
{
  "document_settings": {
    "source_file": "工作原理.md",
    "supported_extensions": [".md", ".txt"]
  }
}
```

- `source_file`: 源文档路径（支持 .md 和 .txt 格式）
- `supported_extensions`: 支持的文件扩展名列表
- **输出文件**: 自动根据输入文件名生成，格式为 `{filename}_expanded{extension}`

#### 标题处理配置
在 `config.json` 中通过 `title_settings` 配置标题处理级别：

```json
{
  "title_settings": {
    "title_level": 6,
    "supported_levels": [5, 6]
  }
}
```

- `title_level`: 标题处理级别
  - `5`: 处理五级标题 (## 1.2.1.3.1 格式)
  - `6`: 处理六级标题 (### 1.2.1.3.1.1 格式)

### 3. 执行方式

#### 方式一：直接运行Python脚本
```bash
cd /home/xiaoting/biaoshu
python3 concurrent_expand.py
```

#### 方式二：使用执行脚本
```bash
cd /home/xiaoting/biaoshu
chmod +x run_expansion.sh
./run_expansion.sh
```

#### 方式三：测试配置功能
```bash
# 测试文档配置功能
python3 test_configurable_documents.py

# 测试标题提取功能
python3 test_title_extraction.py

# 测试单独文件保存功能
python3 test_individual_save.py

# 演示标题级别切换
python3 demo_title_switch.py
```

### 4. 输出结果
程序会：
- 在控制台实时显示处理进度
- 生成详细的日志文件 `expansion_detailed_log.txt`
- 自动创建输出文件 `{source_filename}_expanded.{extension}`
- **为每个章节生成独立的TXT文件**，格式为 `chapter_{编号}._{标题名称}.txt`
- 在控制台打印最终的统计报告

### 5. 当前配置
- 使用阿里云通义千问(Qwen-Plus)模型
- 目标字数：3000-4000字/章节
- 写作风格：技术规范
- 并发请求数：3个
- 默认文档：工作原理.md
- 默认标题级别：6级标题

### 6. 功能特性

#### 文档处理灵活性
- ✅ 支持配置不同的源文档
- ✅ 自动根据源文件名生成输出文件名（`{filename}_expanded{extension}`）
- ✅ 支持 Markdown (.md) 和文本 (.txt) 格式
- ✅ 可灵活切换处理不同的文档文件

#### 单独文件保存
- ✅ 每个生成的章节内容自动保存为独立TXT文件
- ✅ 文件命名格式：`chapter_{编号}._{标题名称}.txt`
- ✅ 文件内容包含标题信息和章节编号
- ✅ 同时追加到主输出文件中

#### 标题处理灵活性
- ✅ 支持五级标题 (## 1.2.1.3.1) 和六级标题 (### 1.2.1.3.1.1) 提取
- ✅ 可通过配置文件灵活切换处理级别
- ✅ 自动检测文档中存在的标题级别
- ✅ 智能提示建议的处理级别

#### 并发处理优化
- ✅ 3个并发请求限制，避免API过载
- ✅ 指数退避重试机制
- ✅ 即时保存生成内容，防止进度丢失

#### 配置驱动设计
- ✅ 通过 `config.json` 统一管理所有配置
- ✅ 支持API密钥环境变量配置
- ✅ 可配置的超时时间和并发限制

### 7. 使用示例

#### 处理text.md文件
```json
// config.json
{
  "document_settings": {
    "source_file": "text.md",
    "supported_extensions": [".md", ".txt"]
  },
  "title_settings": {
    "title_level": 5
  }
}
```
输出文件将自动生成为: `text_expanded.md`

生成的单独文件示例：
- `chapter_1.2.5.1._基于百亿模型的数据蒸馏流程.txt`
- `chapter_1.2.5.1.1._教师模型选型与蒸馏环境配置.txt`
- `chapter_1.2.5.2._增量预训练实施与收敛控制.txt`

#### 处理工作原理.md文件
```json
// config.json  
{
  "document_settings": {
    "source_file": "工作原理.md",
    "supported_extensions": [".md", ".txt"]
  },
  "title_settings": {
    "title_level": 6
  }
}
```
输出文件将自动生成为: `工作原理_expanded.md`

生成的单独文件示例：
- `chapter_1.2.1.3.1.1._自注意力机制的信息聚合原理.txt`
- `chapter_1.2.1.3.1.2._多头注意力的并行特征空间解析.txt`

### 8. 故障排除

如果遇到文档处理问题：
1. 检查 `config.json` 中的 `document_settings` 配置
2. 确认源文档文件存在且可读
3. 运行 `python3 test_configurable_documents.py` 验证配置
4. 查看控制台输出的文件读取信息