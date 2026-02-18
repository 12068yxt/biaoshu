#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API失败诊断工具
分析具体失败原因并提供针对性解决方案
"""

import asyncio
import aiohttp
import json
import os
import time
import random
from datetime import datetime
from typing import List, Dict

class APIDiagnosticTool:
    def __init__(self):
        self.api_key = os.getenv("ALIYUN_API_KEY")
        self.test_results = []
        self.error_patterns = {}
    
    async def test_single_call(self, session: aiohttp.ClientSession, test_name: str, prompt: str) -> Dict:
        """测试单次API调用"""
        print(f"\n🔬 测试: {test_name}")
        start_time = time.time()
        
        if not self.api_key:
            return {"test": test_name, "status": "error", "message": "API密钥未设置"}
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'qwen-plus',
            'input': {
                'prompt': prompt
            },
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 500  # 减少token数加快测试
            }
        }
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        try:
            timeout = aiohttp.ClientTimeout(total=60, connect=30, sock_read=30)
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    content = result.get('output', {}).get('text', '')
                    print(f"✅ 成功 (响应时间: {response_time:.2f}s, 内容长度: {len(content)})")
                    return {
                        "test": test_name,
                        "status": "success",
                        "response_time": response_time,
                        "content_length": len(content)
                    }
                else:
                    error_text = await response.text()
                    print(f"❌ 失败: HTTP {response.status} - {error_text[:100]}")
                    error_type = self.categorize_error(response.status, error_text)
                    return {
                        "test": test_name,
                        "status": "failed",
                        "http_status": response.status,
                        "error_message": error_text[:200],
                        "error_type": error_type,
                        "response_time": response_time
                    }
                    
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ 异常: {str(e)}")
            error_type = self.categorize_exception(str(e))
            return {
                "test": test_name,
                "status": "exception",
                "error_message": str(e),
                "error_type": error_type,
                "response_time": response_time
            }
    
    def categorize_error(self, status_code: int, error_text: str) -> str:
        """分类HTTP错误"""
        error_text = error_text.lower()
        
        if status_code == 429:
            return "rate_limit"
        elif status_code >= 500:
            return "server_error"
        elif status_code >= 400:
            return "client_error"
        elif "timeout" in error_text:
            return "timeout"
        elif "disconnected" in error_text or "connection" in error_text:
            return "connection"
        else:
            return "other"
    
    def categorize_exception(self, error_msg: str) -> str:
        """分类异常"""
        error_msg = error_msg.lower()
        
        if "timeout" in error_msg:
            return "timeout"
        elif "disconnected" in error_msg or "connection" in error_msg:
            return "connection"
        elif "ssl" in error_msg:
            return "ssl_error"
        else:
            return "other_exception"
    
    async def run_comprehensive_diagnosis(self):
        """运行综合诊断"""
        print("🏥 API健康诊断工具")
        print("="*40)
        print(f"🕐 诊断开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试用例
        test_cases = [
            {
                "name": "基础连通性测试",
                "prompt": "请回复'连接正常'"
            },
            {
                "name": "中文处理能力测试",
                "prompt": "请用中文简要介绍人工智能"
            },
            {
                "name": "技术内容测试",
                "prompt": "请简述深度学习的基本原理"
            },
            {
                "name": "长内容生成测试",
                "prompt": "请详细解释神经网络的工作原理，至少200字"
            }
        ]
        
        timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=60)
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            print("\n🚀 开始API诊断测试...")
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n--- 测试 {i}/{len(test_cases)} ---")
                result = await self.test_single_call(session, test_case["name"], test_case["prompt"])
                self.test_results.append(result)
                
                # 记录错误模式
                if result["status"] != "success":
                    error_type = result.get("error_type", "unknown")
                    if error_type not in self.error_patterns:
                        self.error_patterns[error_type] = []
                    self.error_patterns[error_type].append(result)
                
                # 测试间隔
                if i < len(test_cases):
                    await asyncio.sleep(random.uniform(2, 5))
        
        self.generate_diagnosis_report()
    
    def generate_diagnosis_report(self):
        """生成诊断报告"""
        print("\n" + "="*50)
        print("📋 API诊断报告")
        print("="*50)
        
        # 成功率统计
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["status"] == "success")
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 测试总数: {total_tests}")
        print(f"✅ 成功次数: {successful_tests}")
        print(f"❌ 失败次数: {total_tests - successful_tests}")
        print(f"🎯 成功率: {success_rate:.1f}%")
        
        # 响应时间分析
        successful_results = [r for r in self.test_results if r["status"] == "success"]
        if successful_results:
            avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
            print(f"⏱️ 平均响应时间: {avg_response_time:.2f}秒")
        
        # 错误模式分析
        if self.error_patterns:
            print("\n🚨 错误模式分析:")
            for error_type, errors in self.error_patterns.items():
                error_names = {
                    "rate_limit": "速率限制",
                    "server_error": "服务器错误", 
                    "client_error": "客户端错误",
                    "timeout": "超时错误",
                    "connection": "连接错误",
                    "ssl_error": "SSL错误",
                    "other": "其他错误",
                    "other_exception": "其他异常"
                }
                chinese_name = error_names.get(error_type, error_type)
                print(f"  • {chinese_name}: {len(errors)}次")
                
                # 显示具体错误示例
                sample_error = errors[0]
                print(f"    示例: {sample_error.get('error_message', 'N/A')[:100]}...")
        
        # 建议和解决方案
        print("\n💡 改进建议:")
        
        if success_rate >= 80:
            print("✅ API服务基本正常，可以正常使用")
        elif success_rate >= 50:
            print("⚠ API服务不稳定，建议:")
            print("  • 降低并发请求数")
            print("  • 增加重试次数")
            print("  • 延长等待间隔")
        else:
            print("❌ API服务严重不稳定，建议:")
            print("  • 检查网络连接")
            print("  • 验证API密钥有效性")
            print("  • 联系阿里云技术支持")
        
        # 针对性的解决方案
        if "rate_limit" in self.error_patterns:
            print("\n🔧 针对速率限制的解决方案:")
            print("  • 在config.json中设置更低的concurrent_requests值")
            print("  • 增加retry_attempts到10次以上")
            print("  • 使用stable_expand.py单线程版本")
        
        if "connection" in self.error_patterns or "timeout" in self.error_patterns:
            print("\n🔧 针对连接问题的解决方案:")
            print("  • 检查网络稳定性")
            print("  • 增加超时设置")
            print("  • 在不同时间段重试")

def main():
    """主函数"""
    tool = APIDiagnosticTool()
    asyncio.run(tool.run_comprehensive_diagnosis())

if __name__ == "__main__":
    main()