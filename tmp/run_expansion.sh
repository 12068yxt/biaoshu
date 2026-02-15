#!/bin/bash
# 设置阿里云API密钥
export ALIYUN_API_KEY="sk-19278db0ad4b436d9bf381e0c04c56dc"

# 运行扩充程序
echo "正在启动内容扩充程序..."
echo "阿里云API密钥已设置"
echo "=================================="

cd /home/xiaoting/biaoshu
python3 expand.py

echo "=================================="
echo "程序执行完成"