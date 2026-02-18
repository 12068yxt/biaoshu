#!/bin/bash

# PPT SVG生成一键执行脚本

echo "========================================="
echo "     PPT风格SVG生成器"
echo "========================================="
echo ""

# 检查环境变量
if [ -z "$ALIYUN_API_KEY" ]; then
    echo "❌ 错误: 请先设置阿里云API密钥环境变量"
    echo "   export ALIYUN_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

echo "✅ API密钥已设置"
echo ""

# 检查Python依赖
echo "🔍 检查Python依赖..."

REQUIRED_PACKAGES=("aiohttp" "python-pptx")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        MISSING_PACKAGES+=($package)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "⚠️  缺少以下Python包:"
    for pkg in "${MISSING_PACKAGES[@]}"; do
        echo "   - $pkg"
    done
    echo ""
    echo "💡 安装建议:"
    echo "   pip3 install aiohttp python-pptx"
    echo ""
    read -p "是否继续执行? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ 所有依赖包已安装"
fi

echo ""

# 步骤1: 生成SVG文件
echo "🎨 步骤1: 生成PPT风格SVG文件..."
echo "----------------------------------------"

python3 simple_svg_generator.py

if [ $? -ne 0 ]; then
    echo "❌ SVG生成失败"
    exit 1
fi

echo ""
echo "✅ SVG文件生成完成"
echo ""

# 步骤2: 导入到PPT
echo "📊 步骤2: 创建PowerPoint演示文稿..."
echo "----------------------------------------"

python3 ppt_importer.py

if [ $? -ne 0 ]; then
    echo "⚠️  PPT导入可能部分失败，但HTML版本已生成"
fi

echo ""
echo "🎉 全部完成!"
echo ""
echo "📁 输出文件位置:"
echo "   SVG文件: ./generated_svgs/"
echo "   PPT文件: ./ppt_presentations/"
echo ""
echo "📝 注意事项:"
echo "   - 生成的SVG可以直接在浏览器中查看"
echo "   - PowerPoint文件可在Microsoft PowerPoint中打开"
echo "   - HTML版本可在任何浏览器中全屏演示"
echo ""