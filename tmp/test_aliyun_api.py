#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阿里云API连接
"""

import asyncio
import aiohttp
import json
import os

async def test_aliyun_api():
    api_key = "sk-19278db0ad4b436d9bf381e0c04c56dc"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'qwen-plus',
        'input': {
            'prompt': '请简单介绍一下Transformer架构'
        },
        'parameters': {
            'max_tokens': 200,
            'temperature': 0.7
        }
    }
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                print(f"状态码: {response.status}")
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    print("成功!")
                    print(f"生成内容: {result.get('output', {}).get('text', '')}")
                else:
                    print(f"错误: {response_text}")
                    
    except Exception as e:
        print(f"异常: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_aliyun_api())