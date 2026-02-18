# 🚀 快速开始指南

## 5分钟快速上手

### 第1步：环境准备 (1分钟)
```bash
# 设置API密钥（替换为你的实际密钥）
export ALIYUN_API_KEY="sk-19278db0ad4b436d9bf381e0c04c56dc"

# 安装必要依赖
pip3 install aiohttp python-pptx cairosvg
```

### 第2步：查看演示效果 (1分钟)
```bash
# 生成示例文件（无需API密钥）
python3 demo_svg_generation.py

# 查看生成的文件
ls -la demo_svgs/
```

### 第3步：一键生成完整PPT (3分钟)
```bash
# 给脚本添加执行权限
chmod +x run_ppt_generation.sh

# 运行一键生成
./run_ppt_generation.sh
```

## 📋 输出文件说明

生成的文件将位于：
- **SVG文件**: `generated_svgs/` 目录
- **PPT文件**: `ppt_presentations/` 目录
- **演示页面**: HTML格式可在浏览器中查看

## 💡 小贴士

### 查看进度
```bash
# 查看处理进度
cat svg_progress.json
```

### 重新处理特定文件
删除对应的进度记录，然后重新运行脚本

### 自定义配置
编辑 `ppt_config.json` 文件调整样式和参数

## ❓ 常见问题

**Q: 没有API密钥怎么办？**
A: 可以先运行演示脚本 `python3 demo_svg_generation.py` 查看效果

**Q: 生成的文件在哪里？**
A: SVG文件在 `generated_svgs/`，PPT文件在 `ppt_presentations/`

**Q: 如何在PPT中使用？**
A: 直接在PowerPoint中打开生成的 `.pptx` 文件即可

**Q: 支持哪些操作系统？**
A: 支持Windows、macOS、Linux等所有支持Python的系统

---

🎯 **现在就开始创建你的专业演示文稿吧！**