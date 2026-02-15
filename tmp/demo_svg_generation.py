#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG生成演示脚本
展示不依赖API的SVG生成效果
"""

import os
import re
from datetime import datetime

def create_demo_svg(title: str, content: str) -> str:
    """创建演示用的SVG"""
    # 截取合适长度的文本
    display_title = title[:60] + "..." if len(title) > 60 else title
    display_content = content[:300] + "..." if len(content) > 300 else content
    
    # 专业配色方案
    colors = {
        'primary': '#2563eb',      # 蓝色主色
        'secondary': '#60a5fa',    # 浅蓝色
        'accent': '#1e40af',       # 深蓝色
        'background': '#f8fafc',   # 浅灰色背景
        'text': '#1e293b',         # 深灰色文字
        'light_text': '#64748b'    # 浅灰色文字
    }
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <!-- 背景渐变 -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{colors['background']}"/>
      <stop offset="100%" stop-color="#e2e8f0"/>
    </linearGradient>
  </defs>
  <rect width="1920" height="1080" fill="url(#bgGradient)"/>
  
  <!-- 装饰性几何图形 -->
  <circle cx="1800" cy="150" r="80" fill="{colors['secondary']}" opacity="0.1"/>
  <circle cx="100" cy="950" r="60" fill="{colors['primary']}" opacity="0.1"/>
  <polygon points="1850,900 1880,950 1820,950" fill="{colors['accent']}" opacity="0.2"/>
  
  <!-- 主标题容器 -->
  <rect x="120" y="120" width="1680" height="160" rx="20" fill="white" stroke="{colors['primary']}" stroke-width="3"/>
  <rect x="120" y="120" width="20" height="160" fill="{colors['primary']}"/>
  
  <!-- 主标题 -->
  <text x="160" y="220" font-family="Arial, Helvetica, sans-serif" font-size="48" font-weight="bold" fill="{colors['text']}">
    {display_title}
  </text>
  
  <!-- 内容区域 -->
  <rect x="120" y="320" width="1680" height="600" rx="15" fill="white" stroke="#e2e8f0" stroke-width="2"/>
  
  <!-- 内容文本 -->
  <text x="160" y="380" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="{colors['text']}">
    {display_content}
  </text>
  
  <!-- 底部信息栏 -->
  <rect x="120" y="950" width="1680" height="60" rx="10" fill="{colors['primary']}" opacity="0.9"/>
  <text x="160" y="990" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="white">
    技术文档可视化展示 - {datetime.now().strftime('%Y-%m-%d')}
  </text>
  
  <!-- 装饰图标 -->
  <g transform="translate(1700, 960)">
    <circle cx="0" cy="0" r="15" fill="white" opacity="0.3"/>
    <circle cx="30" cy="0" r="12" fill="white" opacity="0.2"/>
    <circle cx="60" cy="0" r="10" fill="white" opacity="0.1"/>
  </g>
</svg>'''
    
    return svg

def generate_sample_svgs():
    """生成示例SVG文件"""
    # 创建输出目录
    output_dir = "demo_svgs"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 生成演示SVG文件...")
    
    # 示例数据
    samples = [
        {
            "filename": "chapter_01_1.2.1.3.1.1_自注意力机制的信息聚合原理.txt",
            "title": "1.2.1.3.1.1 自注意力机制的信息聚合原理",
            "content": "自注意力机制作为当前大语言模型架构中信息聚合过程的核心范式，其内在原理绝非简单地对输入序列各位置进行加权求和这一表层理解所能涵盖；它本质上是一种动态构建全局依赖关系图谱的、具有高度上下文敏感性的、可学习的序列内关系建模方法..."
        },
        {
            "filename": "chapter_02_1.2.1.3.1.2_多头注意力的并行特征空间解析.txt", 
            "title": "1.2.1.3.1.2 多头注意力的并行特征空间解析",
            "content": "多头注意力机制通过并行计算多个注意力头，使模型能够在不同表示子空间中同时捕获多样化的语义关系。每个注意力头专注于特定类型的依赖关系，如句法关系、语义关系或位置关系..."
        },
        {
            "filename": "chapter_03_1.2.1.3.1.3_层级抽象与特征层次化构建机制.txt",
            "title": "1.2.1.3.1.3 层级抽象与特征层次化构建机制", 
            "content": "Transformer架构通过多层堆叠实现特征的层次化抽象，底层网络捕获局部模式和基础语法结构，中间层整合短语级语义，高层网络则建模复杂的语义关系和篇章级结构..."
        }
    ]
    
    generated_files = []
    
    for i, sample in enumerate(samples, 1):
        # 生成SVG
        svg_content = create_demo_svg(sample["title"], sample["content"])
        
        # 创建安全的文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', sample["title"])[:40]
        svg_filename = f"demo_slide_{i:03d}_{safe_title}.svg"
        svg_path = os.path.join(output_dir, svg_filename)
        
        # 保存文件
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        generated_files.append(svg_path)
        print(f"✅ 生成: {svg_filename}")
    
    print(f"\n🎉 演示完成！生成了 {len(generated_files)} 个SVG文件")
    print(f"📁 文件位置: {os.path.abspath(output_dir)}")
    print("\n💡 查看方式:")
    print("   1. 在浏览器中直接打开SVG文件")
    print("   2. 使用图像查看器")
    print("   3. 导入到PowerPoint或其他演示软件")
    
    return generated_files

def create_demo_html(svgs: list):
    """创建演示用的HTML页面"""
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVG演示 - 技术文档可视化</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .svg-preview {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .svg-preview:hover {
            transform: translateY(-5px);
        }
        .svg-preview img {
            width: 100%;
            height: auto;
            border-radius: 5px;
        }
        .svg-title {
            font-size: 16px;
            font-weight: bold;
            margin: 10px 0 5px 0;
            color: #2d3748;
        }
        .svg-path {
            font-size: 12px;
            color: #718096;
            word-break: break-all;
        }
        .instructions {
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .instructions h2 {
            color: #2d3748;
            margin-top: 0;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .feature {
            background: #edf2f7;
            padding: 15px;
            border-radius: 8px;
        }
        .feature h3 {
            margin: 0 0 10px 0;
            color: #2b6cb0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 技术文档SVG可视化演示</h1>
        
        <div class="gallery">
'''

    for svg_path in svgs:
        filename = os.path.basename(svg_path)
        title = filename.replace('demo_slide_', '').replace('_', ' ').replace('.svg', '')
        html_content += f'''
            <div class="svg-preview">
                <img src="{svg_path}" alt="{title}">
                <div class="svg-title">{title}</div>
                <div class="svg-path">{svg_path}</div>
            </div>
'''

    html_content += '''
        </div>
        
        <div class="instructions">
            <h2>📋 使用说明</h2>
            <div class="feature-list">
                <div class="feature">
                    <h3>🖥️ 浏览器查看</h3>
                    <p>直接在浏览器中打开SVG文件，支持缩放和高清显示</p>
                </div>
                <div class="feature">
                    <h3>📊 PPT导入</h3>
                    <p>将SVG文件导入PowerPoint，每张幻灯片对应一个章节</p>
                </div>
                <div class="feature">
                    <h3>🌐 HTML演示</h3>
                    <p>使用我们提供的HTML演示框架进行全屏展示</p>
                </div>
                <div class="feature">
                    <h3>📱 响应式设计</h3>
                    <p>1920×1080分辨率，完美适配各种显示设备</p>
                </div>
            </div>
            
            <h3>🚀 下一步</h3>
            <p>运行完整版生成器处理所有72个章节：</p>
            <pre><code>export ALIYUN_API_KEY="your-api-key"
python3 simple_svg_generator.py</code></pre>
        </div>
    </div>
</body>
</html>'''

    # 保存HTML文件
    html_path = "demo_svgs/demo_gallery.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"🌐 HTML演示页面已创建: {html_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("     SVG可视化演示生成器")
    print("=" * 60)
    
    # 生成演示SVG
    svgs = generate_sample_svgs()
    
    # 创建HTML演示页面
    create_demo_html(svgs)
    
    print("\n" + "=" * 60)
    print("✅ 演示生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()