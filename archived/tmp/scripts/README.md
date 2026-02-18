# 📚 文档智能扩充工具集

## 🎯 脚本位置变更通知

根据用户偏好，所有脚本文件已统一移动到 `/home/xiaoting/biaoshu/tmp/scripts/` 目录下进行管理。

## 🚀 使用说明

### 进入脚本目录
```bash
cd /home/xiaoting/biaoshu/tmp/scripts
```

### 查看可用脚本
```bash
ls -la *.py
```

### 运行智能跳过处理（推荐）
```bash
uv run python smart_skip_expand.py
```

### 其他处理选项
- `stable_expand.py` - 稳定单线程版（最高成功率）
- `progressive_expand.py` - 渐进式批量处理
- `diagnose_failures.py` - API状态诊断工具

## 📖 详细文档
请查看各脚本目录下的使用说明文档获取详细信息。
