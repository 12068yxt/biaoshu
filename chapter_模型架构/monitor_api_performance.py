#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API性能监控脚本
用于跟踪API调用成功率和识别失败模式
"""

import asyncio
import aiohttp
import time
import json
from collections import defaultdict, deque
from datetime import datetime

class APIMonitor:
    def __init__(self):
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'error_types': defaultdict(int),
            'response_times': deque(maxlen=100),
            'recent_errors': deque(maxlen=20)
        }
        self.start_time = time.time()
    
    def record_call(self, success: bool, response_time: float = None, error_msg: str = None):
        """记录API调用结果"""
        self.stats['total_calls'] += 1
        
        if success:
            self.stats['successful_calls'] += 1
            if response_time:
                self.stats['response_times'].append(response_time)
        else:
            self.stats['failed_calls'] += 1
            if error_msg:
                # 分类错误
                error_type = self.classify_error(error_msg)
                self.stats['error_types'][error_type] += 1
                self.stats['recent_errors'].append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'error': error_msg,
                    'type': error_type
                })
    
    def classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        error_msg = error_msg.lower()
        if "server disconnected" in error_msg or "connection" in error_msg:
            return "连接错误"
        elif "timeout" in error_msg:
            return "超时错误"
        elif "429" in error_msg or "rate limit" in error_msg:
            return "速率限制"
        elif "50" in error_msg:
            return "服务器错误"
        elif "40" in error_msg:
            return "客户端错误"
        else:
            return "其他错误"
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        success_rate = (self.stats['successful_calls'] / self.stats['total_calls'] * 100) if self.stats['total_calls'] > 0 else 0
        
        avg_response_time = 0
        if self.stats['response_times']:
            avg_response_time = sum(self.stats['response_times']) / len(self.stats['response_times'])
        
        uptime = time.time() - self.start_time
        
        return {
            '总调用次数': self.stats['total_calls'],
            '成功次数': self.stats['successful_calls'],
            '失败次数': self.stats['failed_calls'],
            '成功率': f"{success_rate:.1f}%",
            '平均响应时间': f"{avg_response_time:.2f}秒",
            '运行时间': f"{uptime:.0f}秒",
            '错误分类': dict(self.stats['error_types']),
            '最近错误': list(self.stats['recent_errors'])
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("📊 API调用统计报告")
        print("="*50)
        print(f"📈 总调用次数: {stats['总调用次数']}")
        print(f"✅ 成功次数: {stats['成功次数']}")
        print(f"❌ 失败次数: {stats['失败次数']}")
        print(f"🎯 成功率: {stats['成功率']}")
        print(f"⏱️ 平均响应时间: {stats['平均响应时间']}")
        print(f"⏰ 运行时间: {stats['运行时间']}")
        
        if stats['错误分类']:
            print("\n🚨 错误分类统计:")
            for error_type, count in stats['错误分类'].items():
                print(f"  • {error_type}: {count}次")
        
        if stats['最近错误']:
            print("\n📝 最近错误记录:")
            for error in stats['最近错误'][-5:]:  # 显示最后5个错误
                print(f"  [{error['time']}] {error['type']}: {error['error']}")

# 测试API连接的简单函数
async def test_api_connection(api_key: str, monitor: APIMonitor):
    """测试单次API连接"""
    if not api_key:
        print("❌ 未设置API密钥")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'qwen-plus',
        'input': {
            'prompt': '请回复"测试成功"'
        },
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 100
        }
    }
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    start_time = time.time()
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    content = result.get('output', {}).get('text', '')
                    monitor.record_call(True, response_time)
                    print(f"✅ API连接测试成功 (响应时间: {response_time:.2f}s)")
                    return True
                else:
                    error_text = await response.text()
                    monitor.record_call(False, response_time, f"HTTP {response.status}: {error_text[:100]}")
                    print(f"❌ API连接测试失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        response_time = time.time() - start_time
        monitor.record_call(False, response_time, str(e))
        print(f"❌ API连接测试异常: {str(e)}")
        return False

async def continuous_monitor(api_key: str, interval: int = 10):
    """持续监控API性能"""
    monitor = APIMonitor()
    print("🚀 开始API性能监控...")
    print(f"📡 监控间隔: {interval}秒")
    print("按 Ctrl+C 停止监控\n")
    
    try:
        while True:
            await test_api_connection(api_key, monitor)
            monitor.print_stats()
            await asyncio.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n⚠ 监控已停止")
        monitor.print_stats()

def main():
    """主函数"""
    import os
    
    api_key = os.getenv("ALIYUN_API_KEY")
    if not api_key:
        print("❌ 请先设置 ALIYUN_API_KEY 环境变量")
        print("示例: export ALIYUN_API_KEY='your_api_key'")
        return
    
    print("🤖 API性能监控工具")
    print("="*30)
    
    # 询问用户选择监控模式
    print("请选择监控模式:")
    print("1. 单次测试")
    print("2. 持续监控")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        monitor = APIMonitor()
        asyncio.run(test_api_connection(api_key, monitor))
        monitor.print_stats()
    elif choice == "2":
        interval = input("请输入监控间隔秒数 (默认10): ").strip()
        interval = int(interval) if interval.isdigit() else 10
        asyncio.run(continuous_monitor(api_key, interval))
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()