#!/bin/bash

# SVG生成器运行脚本

set -e  # 遇到错误时退出

echo "=== PPT SVG生成器 ==="
echo "当前时间: $(date)"

# 检查API密钥
if [ -z "$ALIYUN_API_KEY" ]; then
    echo "错误: 未设置 ALIYUN_API_KEY 环境变量"
    echo "请先执行: export ALIYUN_API_KEY='your-api-key'"
    exit 1
fi

echo "API密钥已设置"

# 检查依赖
if ! python -c "import aiohttp" &> /dev/null; then
    echo "安装依赖..."
    pip install aiohttp
fi

# 根据参数选择运行模式
case "${1:-batch}" in
    "debug")
        echo "运行调试模式..."
        python ppt_svg_generator.py --mode debug
        ;;
    "test")
        echo "运行测试模式..."
        shift
        python ppt_svg_generator.py --mode test "$@"
        ;;
    "list")
        echo "列出可用提示词..."
        python ppt_svg_generator.py --list-prompts
        ;;
    "batch"|*)
        echo "运行批量生成模式..."
        python ppt_svg_generator.py --mode batch
        ;;
esac

echo "=== 运行完成 ==="
echo "输出文件位于: ../generated_svgs/"
echo "日志文件: svg_generation.log"