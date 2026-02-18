#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控扩充程序的进度
"""

import time
import os
from datetime import datetime

def monitor_progress():
    log_file = "expansion_detailed_log.txt"
    last_size = 0
    
    print("开始监控扩充进度...")
    print("="*50)
    
    while True:
        try:
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                
                if current_size > last_size:
                    # 读取新增的日志内容
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_content = f.read()
                    
                    if new_content:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 新增日志:")
                        print(new_content)
                        print("-" * 30)
                    
                    last_size = current_size
            
            # 检查是否生成了输出文件
            output_files = ["工作原理_扩充版.md", "expansion_summary.txt"]
            for output_file in output_files:
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {output_file}: {file_size} 字节")
            
            time.sleep(5)  # 每5秒检查一次
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"监控出错: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_progress()