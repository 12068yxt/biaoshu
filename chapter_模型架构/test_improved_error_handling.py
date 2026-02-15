#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进的错误处理功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from concurrent_expand import ConcurrentDocumentExpander
import asyncio

def test_error_classification():
    """测试错误分类功能"""
    print("🧪 测试错误分类功能...")
    
    expander = ConcurrentDocumentExpander()
    
    test_cases = [
        ("Server disconnected", "connection"),
        ("Connection timeout", "connection"),
        ("Read timeout", "timeout"),
        ("HTTP 429 Too Many Requests", "rate_limit"),
        ("Rate limit exceeded", "rate_limit"),
        ("HTTP 500 Internal Server Error", "server_error"),
        ("HTTP 503 Service Unavailable", "server_error"),
        ("Unknown error occurred", "other")
    ]
    
    all_passed = True
    for error_msg, expected_type in test_cases:
        actual_type = expander.classify_error(error_msg)
        status = "✅" if actual_type == expected_type else "❌"
        print(f"{status} '{error_msg}' -> {actual_type} (期望: {expected_type})")
        if actual_type != expected_type:
            all_passed = False
    
    print(f"\n{'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    return all_passed

async def test_api_monitoring():
    """测试API监控功能"""
    print("\n🧪 测试API监控功能...")
    
    # 这里可以添加实际的API测试，但现在只是演示监控类的使用
    try:
        from monitor_api_performance import APIMonitor
        monitor = APIMonitor()
        
        # 模拟一些API调用
        monitor.record_call(True, 1.5)
        monitor.record_call(True, 2.1)
        monitor.record_call(False, 3.0, "Server disconnected")
        monitor.record_call(False, 2.5, "Timeout error")
        
        stats = monitor.get_stats()
        print("📊 监控统计测试:")
        for key, value in stats.items():
            if key != '最近错误':  # 跳过复杂的嵌套结构
                print(f"  {key}: {value}")
        
        print("✅ API监控功能正常")
        return True
        
    except Exception as e:
        print(f"❌ API监控测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 改进功能测试套件")
    print("="*40)
    
    # 测试错误分类
    classification_ok = test_error_classification()
    
    # 测试API监控
    monitoring_ok = asyncio.run(test_api_monitoring())
    
    print("\n" + "="*40)
    print("🏁 测试总结:")
    print(f"错误分类测试: {'✅ 通过' if classification_ok else '❌ 失败'}")
    print(f"API监控测试: {'✅ 通过' if monitoring_ok else '❌ 失败'}")
    
    overall_success = classification_ok and monitoring_ok
    print(f"总体结果: {'🎉 所有测试通过' if overall_success else '💥 部分测试失败'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit(main())