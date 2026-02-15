#!/bin/bash

# 小标题处理运行脚本
# 自动化处理文档中的小标题内容生成

set -e  # 遇到错误时退出

echo "========================================="
echo "小标题处理系统启动"
echo "========================================="

# 检查环境变量
if [ -z "$ALIYUN_API_KEY" ]; then
    echo "错误: 未设置 ALIYUN_API_KEY 环境变量"
    echo "请执行: export ALIYUN_API_KEY='your_api_key'"
    exit 1
fi

echo "✓ API密钥已设置"

# 检查必要文件
if [ ! -f "模型架构.md" ]; then
    echo "错误: 未找到源文档 模型架构.md"
    exit 1
fi

if [ ! -f "config.json" ]; then
    echo "错误: 未找到配置文件 config.json"
    exit 1
fi

echo "✓ 必要文件检查通过"

# 创建输出目录
mkdir -p output
echo "✓ 输出目录准备就绪"

# 运行功能选择
echo ""
echo "请选择要执行的功能:"
echo "1) 标题解析测试"
echo "2) 功能演示"
echo "3) 完整文档处理"
echo "4) 小标题专门处理"
echo "5) 所有功能依次执行"
echo ""

read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "运行标题解析测试..."
        python test_subtitle_extraction.py
        ;;
    2)
        echo "运行功能演示..."
        python demo_subtitle_processing.py
        ;;
    3)
        echo "开始完整文档处理..."
        python concurrent_expand.py
        ;;
    4)
        echo "开始小标题专门处理..."
        python subtitle_processor.py
        ;;
    5)
        echo "依次执行所有功能..."
        echo "1. 标题解析测试"
        python test_subtitle_extraction.py
        
        echo "2. 功能演示"
        python demo_subtitle_processing.py
        
        echo "3. 完整文档处理"
        python concurrent_expand.py
        
        echo "4. 小标题专门处理"
        python subtitle_processor.py
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "处理完成"
echo "========================================="

# 显示结果
if ls *_expanded.md 1> /dev/null 2>&1; then
    echo "生成的主要文件:"
    ls -la *_expanded.md
fi

if ls chapter_*._*.md 1> /dev/null 2>&1; then
    echo "生成的章节文件数量:"
    ls chapter_*._*.md | wc -l
fi

echo "处理日志已保存到相关文件中"